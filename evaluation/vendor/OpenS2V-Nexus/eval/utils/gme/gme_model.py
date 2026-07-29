from __future__ import annotations

import base64
import logging
import math
import os
from io import BytesIO
from typing import Dict, List, Optional

import requests
import torch
from PIL import Image
from torch.utils.data import DataLoader
from tqdm.autonotebook import tqdm
from transformers import AutoModelForVision2Seq, AutoProcessor


class GmeQwen2VL:
    def __init__(
        self,
        model_name: str = "gme-Qwen2-VL-7B-Instruct",
        model_path: Optional[str] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
        min_image_tokens=256,
        max_image_tokens=1280,
        max_length=1800,
        attn_model=None,  # "flash_attention_2"
        **kwargs,
    ) -> None:
        model_name = model_path or model_name
        self.base = AutoModelForVision2Seq.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            attn_implementation=attn_model,
            **kwargs,
        )
        self.base.eval()
        self.normalize = True
        self.device = device
        min_pixels = min_image_tokens * 28 * 28
        max_pixels = max_image_tokens * 28 * 28
        self.max_length = max_length
        self.processor = AutoProcessor.from_pretrained(
            model_name, min_pixels=min_pixels, max_pixels=max_pixels, **kwargs
        )
        if attn_model == "flash_attention_2":
            self.processor.tokenizer.padding_side = "left"
        else:
            self.processor.tokenizer.padding_side = "right"
        self.defualt_instruction = "You are a helpful assistant."
        self.sep = " "

    def forward(
        self,
        input_ids: Optional[torch.LongTensor] = None,
        attention_mask: Optional[torch.Tensor] = None,
        position_ids: Optional[torch.LongTensor] = None,
        past_key_values: Optional[List[torch.FloatTensor]] = None,
        inputs_embeds: Optional[torch.FloatTensor] = None,
        pixel_values: Optional[torch.Tensor] = None,
        # pixel_values_videos: Optional[torch.FloatTensor] = None,
        image_grid_thw: Optional[torch.LongTensor] = None,
        # video_grid_thw: Optional[torch.LongTensor] = None,
        pooling_mask: Optional[torch.LongTensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        if inputs_embeds is None:
            inputs_embeds = self.base.model.embed_tokens(input_ids)
            if pixel_values is not None:
                pixel_values = pixel_values.type(self.base.visual.get_dtype())
                image_embeds = self.base.visual(
                    pixel_values, grid_thw=image_grid_thw
                ).to(inputs_embeds.device)
                image_mask = input_ids == self.base.config.image_token_id
                inputs_embeds[image_mask] = image_embeds
            # if pixel_values_videos is not None:
            #     pixel_values_videos = pixel_values_videos.type(self.base.visual.get_dtype())
            #     video_embeds = self.base.visual(pixel_values_videos, grid_thw=video_grid_thw).to(inputs_embeds.device)
            #     video_mask = input_ids == self.base.config.video_token_id
            #     inputs_embeds[video_mask] = video_embeds
            if attention_mask is not None:
                attention_mask = attention_mask.to(inputs_embeds.device)

        outputs = self.base.model(
            input_ids=None,
            position_ids=position_ids,
            attention_mask=attention_mask,
            past_key_values=past_key_values,
            inputs_embeds=inputs_embeds,
        )

        pooling_mask = attention_mask if pooling_mask is None else pooling_mask
        left_padding = pooling_mask[:, -1].sum() == pooling_mask.shape[0]  # TODO
        if left_padding:
            embeddings = outputs.last_hidden_state[:, -1]
        else:
            sequence_lengths = pooling_mask.sum(dim=1) - 1
            batch_size = outputs.last_hidden_state.shape[0]
            embeddings = outputs.last_hidden_state[
                torch.arange(batch_size, device=outputs.last_hidden_state.device),
                sequence_lengths,
            ]
        if self.normalize:
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings.contiguous()

    def embed(
        self,
        texts: list[str],
        images: list[Image.Image],
        is_query=True,
        instruction=None,
        **kwargs,
    ):
        self.base.to(self.device)
        # Inputs must be batched
        input_texts, input_images = [], []
        for t, i in zip(texts, images):
            if not is_query or instruction is None:
                instruction = self.defualt_instruction
            input_str = ""
            if i is None:
                input_images = None  # All examples in the same batch are consistent
            else:
                input_str += "<|vision_start|><|image_pad|><|vision_end|>"
                i = fetch_image(i)
                input_images.append(i)
            if t is not None:
                input_str += t
            msg = f"<|im_start|>system\n{instruction}<|im_end|>\n<|im_start|>user\n{input_str}<|im_end|>\n<|im_start|>assistant\n<|endoftext|>"
            input_texts.append(msg)

        inputs = self.processor(
            text=input_texts,
            images=input_images,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}  # TODO
        with torch.no_grad():
            embeddings = self.forward(**inputs)
        return embeddings

    def encode(self, sentences: list[str], *, prompt_name=None, **kwargs):
        return self.get_fused_embeddings(
            texts=sentences, prompt_name=prompt_name, **kwargs
        )

    def encode_queries(self, queries: List[str], **kwargs):
        embeddings = self.encode(queries, **kwargs)
        return embeddings

    def encode_corpus(self, corpus: List[Dict[str, str]], **kwargs):
        if type(corpus) is dict:
            sentences = [
                (corpus["title"][i] + self.sep + corpus["text"][i]).strip()
                if "title" in corpus
                else corpus["text"][i].strip()
                for i in range(len(corpus["text"]))
            ]
        else:
            sentences = [
                (doc["title"] + self.sep + doc["text"]).strip()
                if "title" in doc
                else doc["text"].strip()
                for doc in corpus
            ]
        embeddings = self.encode(sentences, is_query=False, **kwargs)
        return embeddings

    def get_image_embeddings(self, images: list[Image.Image] | DataLoader, **kwargs):
        return self.get_fused_embeddings(images=images, **kwargs)

    def get_text_embeddings(self, texts: list[str], **kwargs):
        return self.get_fused_embeddings(texts=texts, **kwargs)

    def get_fused_embeddings(
        self,
        texts: list[str] = None,
        images: list[Image.Image] | DataLoader = None,
        **kwargs,
    ):
        if isinstance(images, DataLoader):
            image_loader = images
            batch_size = image_loader.batch_size
            image_loader.dataset.transform = None
        else:
            batch_size = kwargs.pop("batch_size", 32)
            if images is None:
                image_loader = None
            else:
                image_loader = DataLoader(
                    images,
                    batch_size=batch_size,
                    shuffle=False,
                    collate_fn=custom_collate_fn,
                    num_workers=min(math.floor(os.cpu_count() / 2), 8),
                )

        if texts is None:
            assert image_loader is not None
            n_batch = len(image_loader)
        else:
            n_batch = len(texts) // batch_size + int(len(texts) % batch_size > 0)
            image_loader = image_loader or [None] * n_batch

        all_embeddings = []
        none_batch = [None] * batch_size
        show_progress_bar = kwargs.pop("show_progress_bar", True)
        pbar = tqdm(
            total=n_batch,
            disable=not show_progress_bar,
            mininterval=1,
            miniters=10,
            desc="encode",
        )
        for n, img_batch in zip(
            range(0, n_batch * batch_size, batch_size), image_loader
        ):
            text_batch = none_batch if texts is None else texts[n : n + batch_size]
            img_batch = none_batch if img_batch is None else img_batch
            embeddings = self.embed(texts=text_batch, images=img_batch, **kwargs)
            pbar.update(1)
            all_embeddings.append(embeddings.cpu())
        pbar.close()
        all_embeddings = torch.cat(all_embeddings, dim=0)
        return all_embeddings


def custom_collate_fn(batch):
    return batch


IMAGE_FACTOR = 28
MIN_PIXELS = 4 * 28 * 28
MAX_PIXELS = 16384 * 28 * 28
MAX_RATIO = 200


def round_by_factor(number: int, factor: int) -> int:
    """Returns the closest integer to 'number' that is divisible by 'factor'."""
    return round(number / factor) * factor


def ceil_by_factor(number: int, factor: int) -> int:
    """Returns the smallest integer greater than or equal to 'number' that is divisible by 'factor'."""
    return math.ceil(number / factor) * factor


def floor_by_factor(number: int, factor: int) -> int:
    """Returns the largest integer less than or equal to 'number' that is divisible by 'factor'."""
    return math.floor(number / factor) * factor


def smart_resize(
    height: int,
    width: int,
    factor: int = IMAGE_FACTOR,
    min_pixels: int = MIN_PIXELS,
    max_pixels: int = MAX_PIXELS,
) -> tuple[int, int]:
    """
    Rescales the image so that the following conditions are met:

    1. Both dimensions (height and width) are divisible by 'factor'.

    2. The total number of pixels is within the range ['min_pixels', 'max_pixels'].

    3. The aspect ratio of the image is maintained as closely as possible.
    """
    h_bar = max(factor, round_by_factor(height, factor))
    w_bar = max(factor, round_by_factor(width, factor))
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar = floor_by_factor(height / beta, factor)
        w_bar = floor_by_factor(width / beta, factor)
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar = ceil_by_factor(height * beta, factor)
        w_bar = ceil_by_factor(width * beta, factor)

    if max(h_bar, w_bar) / min(h_bar, w_bar) > MAX_RATIO:
        logging.warning(
            f"Absolute aspect ratio must be smaller than {MAX_RATIO}, got {max(h_bar, w_bar) / min(h_bar, w_bar)}"
        )
        if h_bar > w_bar:
            h_bar = w_bar * MAX_RATIO
        else:
            w_bar = h_bar * MAX_RATIO
    return h_bar, w_bar


def fetch_image(
    image: str | Image.Image, size_factor: int = IMAGE_FACTOR
) -> Image.Image:
    image_obj = None
    if isinstance(image, Image.Image):
        image_obj = image
    elif image.startswith("http://") or image.startswith("https://"):
        image_obj = Image.open(requests.get(image, stream=True).raw)
    elif image.startswith("file://"):
        image_obj = Image.open(image[7:])
    elif image.startswith("data:image"):
        if "base64," in image:
            _, base64_data = image.split("base64,", 1)
            data = base64.b64decode(base64_data)
            image_obj = Image.open(BytesIO(data))
    else:
        image_obj = Image.open(image)
    if image_obj is None:
        raise ValueError(
            f"Unrecognized image input, support local path, http url, base64 and PIL.Image, got {image}"
        )
    image = image_obj.convert("RGB")
    ## resize
    # if "resized_height" in ele and "resized_width" in ele:
    #     resized_height, resized_width = smart_resize(
    #         ele["resized_height"],
    #         ele["resized_width"],
    #         factor=size_factor,
    #     )
    # else:
    width, height = image.size
    # min_pixels = ele.get("min_pixels", MIN_PIXELS)
    # max_pixels = ele.get("max_pixels", MAX_PIXELS)
    resized_height, resized_width = smart_resize(
        height,
        width,
        factor=size_factor,
        min_pixels=MIN_PIXELS,
        max_pixels=MAX_PIXELS,
    )
    image = image.resize((resized_width, resized_height))

    return image


###
