import argparse
import os.path as osp
from tqdm import tqdm

import os
import json
import numpy as np
import supervision as sv
import torch
from mmengine.config import Config, DictAction
from mmengine.dataset import Compose
from mmengine.runner import Runner
from mmengine.runner.amp import autocast
from mmyolo.registry import RUNNERS
from PIL import Image
from torchvision.ops import nms
from transformers import (
    AutoProcessor,
    AutoTokenizer,
    CLIPTextModelWithProjection,
    CLIPVisionModelWithProjection,
)
from utils.gme.gme_model import GmeQwen2VL
import decord

os.environ["TOKENIZERS_PARALLELISM"] = "false"

BOUNDING_BOX_ANNOTATOR = sv.BoundingBoxAnnotator(thickness=2)
MASK_ANNOTATOR = sv.MaskAnnotator()


class LabelAnnotator(sv.LabelAnnotator):
    @staticmethod
    def resolve_text_background_xyxy(center_coordinates, text_wh, position):
        center_x, center_y = center_coordinates
        text_w, text_h = text_wh
        return center_x, center_y, center_x + text_w, center_y + text_h


LABEL_ANNOTATOR = LabelAnnotator(text_padding=4, text_scale=0.5, text_thickness=1)


def sample_video_frames(video_path, num_frames=16):
    vr = decord.VideoReader(video_path)
    total_frames = len(vr)

    if num_frames is None:
        frame_indices = np.arange(total_frames)
    else:
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    frames = []
    for idx in frame_indices:
        frame = vr[int(idx)].asnumpy()
        pil_image = Image.fromarray(frame)
        frames.append(pil_image)

    return frames


def generate_image_embeddings(
    prompt_image, vision_encoder, vision_processor, projector, device="cuda:0"
):
    prompt_image = prompt_image.convert("RGB")
    inputs = vision_processor(images=[prompt_image], return_tensors="pt", padding=True)
    inputs = inputs.to(device)
    image_outputs = vision_encoder(**inputs)
    img_feats = image_outputs.image_embeds.view(1, -1)
    img_feats = img_feats / img_feats.norm(p=2, dim=-1, keepdim=True)
    if projector is not None:
        img_feats = projector(img_feats)
    return img_feats


def run_image(
    runner,
    vision_encoder,
    vision_processor,
    padding_token,
    image,
    text,
    prompt_image,
    add_padding,
    max_num_boxes,
    score_thr,
    nms_thr,
    device="cuda:0" # Add device arg
):
    image = image.convert("RGB")
    if prompt_image is not None:
        texts = [["object"], [" "]]
        projector = None
        if hasattr(runner.model, "image_prompt_encoder"):
            projector = runner.model.image_prompt_encoder.projector
        prompt_embeddings = generate_image_embeddings(
            prompt_image,
            vision_encoder=vision_encoder,
            vision_processor=vision_processor,
            projector=projector,
            device=device # Pass device
        )
        if add_padding == "padding":
            prompt_embeddings = torch.cat([prompt_embeddings, padding_token], dim=0)
        prompt_embeddings = prompt_embeddings / prompt_embeddings.norm(
            p=2, dim=-1, keepdim=True
        )
        runner.model.num_test_classes = prompt_embeddings.shape[0]
        runner.model.setembeddings(prompt_embeddings[None])
    else:
        runner.model.setembeddings(None)
        texts = [[t.strip()] for t in text.split(",")]
    data_info = {"img_id": 0, "img": np.array(image), "texts": texts}
    data_info = runner.pipeline(data_info)
    data_batch = {
        "inputs": data_info["inputs"].unsqueeze(0),
        "data_samples": [data_info["data_samples"]],
    }

    with autocast(enabled=False), torch.no_grad():
        if (prompt_image is not None) and ("texts" in data_batch["data_samples"][0]):
            del data_batch["data_samples"][0]["texts"]
        output = runner.model.test_step(data_batch)[0]
        pred_instances = output.pred_instances

    keep = nms(pred_instances.bboxes, pred_instances.scores, iou_threshold=nms_thr)
    pred_instances = pred_instances[keep]
    pred_instances = pred_instances[pred_instances.scores.float() > score_thr]

    if len(pred_instances.scores) > max_num_boxes:
        indices = pred_instances.scores.float().topk(max_num_boxes)[1]
        pred_instances = pred_instances[indices]

    pred_instances = pred_instances.cpu().numpy()

    return pred_instances


def yoloworld_inference(
    runner,
    vision_encoder,
    vision_processor,
    padding_embed,
    image,
    prompt_image,
    input_text=None,
    add_padding="none",
    max_num_boxes=100,
    score_thr=0.5,
    nms_thr=0.7,
    device="cuda:0" # Add device arg
):
    output_image = run_image(
        runner,
        vision_encoder,
        vision_processor,
        padding_embed,
        image,
        input_text,
        prompt_image,
        add_padding,
        max_num_boxes,
        score_thr,
        nms_thr,
        device=device # Pass device
    )

    return output_image


def load_model_and_config(args, clip_model_path, device):
    cfg = Config.fromfile(args.model_config)
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)

    if args.work_dir is not None:
        cfg.work_dir = args.work_dir
    elif cfg.get("work_dir", None) is None:
        cfg.work_dir = osp.join(
            "./work_dirs", osp.splitext(osp.basename(args.model_config))[0]
        )

    cfg.load_from = args.yolo_model_path
    cfg.text_model_name = clip_model_path
    cfg.model.vision_model = clip_model_path
    cfg.model.backbone.text_model.model_name = clip_model_path

    if "runner_type" not in cfg:
        runner = Runner.from_cfg(cfg)
    else:
        runner = RUNNERS.build(cfg)

    runner.call_hook("before_run")
    runner.load_or_resume()
    pipeline = cfg.test_dataloader.dataset.pipeline
    pipeline[0].type = "mmdet.LoadImageFromNDArray"
    runner.pipeline = Compose(pipeline)
    runner.model.eval()

    yolo_processor = AutoProcessor.from_pretrained(clip_model_path)
    yolo_vision_model = CLIPVisionModelWithProjection.from_pretrained(clip_model_path)
    yolo_vision_model.to(device)

    yolo_tokenizer = AutoTokenizer.from_pretrained(clip_model_path, use_fast=True)
    yolo_text_model = CLIPTextModelWithProjection.from_pretrained(clip_model_path)
    yolo_text_model.to(device)

    texts = [" "]
    texts = yolo_tokenizer(text=texts, return_tensors="pt", padding=True)
    texts = texts.to(device)
    text_outputs = yolo_text_model(**texts)
    txt_feats = text_outputs.text_embeds
    txt_feats = txt_feats / txt_feats.norm(p=2, dim=-1, keepdim=True)
    txt_feats = txt_feats.reshape(-1, txt_feats.shape[-1])
    txt_feats = txt_feats[0].unsqueeze(0)

    return yolo_vision_model, yolo_processor, runner, txt_feats


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_video_folder",
        type=str,
        default="demo_result/model_name_input_video",
    )
    parser.add_argument(
        "--input_image_folder",
        default="BestWishYsh/OpenS2V-Eval",
    )
    parser.add_argument(
        "--input_json_file",
        type=str,
        default="demo_result/input_json/Open-Domain_Eval.json",
    )
    parser.add_argument(
        "--output_json_folder",
        type=str,
        default="demo_result/model_name_output_json",
    )
    parser.add_argument(
        "--model_config",
        default="utils/yoloworld/configs/yolo_world_v2_l_vlpan_bn_2e-4_80e_8gpus_image_prompt_demo.py",
    )
    parser.add_argument(
        "--yolo_model_path",
        default="BestWishYsh/OpenS2V-Weight/yolo_world_v2_l_image_prompt_adapter-719a7afb.pth",
    )
    parser.add_argument(
        "--yolo_clip_model_path",
        default="openai/clip-vit-base-patch32",
    )
    parser.add_argument(
        "--gme_model_path",
        default="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
    )
    parser.add_argument(
        "--work-dir",
        default=None,
    )
    parser.add_argument(
        "--cfg-options",
        nargs="+",
        action=DictAction,
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    # Check for CUDA availability. If not available (e.g. CUDA_VISIBLE_DEVICES=""), fallback to cpu
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    input_video_folder = args.input_video_folder
    input_image_folder = args.input_image_folder
    input_json_file = args.input_json_file
    output_json_folder = args.output_json_folder

    gme_model_path = args.gme_model_path
    yolo_clip_model_path = args.yolo_clip_model_path

    output_json_file = os.path.join(output_json_folder, "nexusscore.json")
    os.makedirs(output_json_folder, exist_ok=True)
    if os.path.exists(output_json_file):
        print("continue")
        return

    yolo_vision_model, yolo_processor, runner, txt_feats = load_model_and_config(
        args, yolo_clip_model_path, device
    )
    # Revert to flash_attention_2 as requested by user
    gme = GmeQwen2VL(gme_model_path, attn_model="flash_attention_2", device=device)

    with open(input_json_file, "r") as f:
        json_data = json.load(f)

    video_files = [f for f in os.listdir(input_video_folder) if f.endswith(".mp4")]

    results = {}
    for video_file in tqdm(video_files, desc="Processing videos"):
        try:
            video_path = os.path.join(input_video_folder, video_file)
            prefix = os.path.splitext(video_file)[0]

            print(f"Processing {prefix}...")
            
            # DEBUG
            if prefix not in json_data:
                print(f"[WARNING] {prefix} not found in input json keys: {list(json_data.keys())[:5]}...")
                continue
                
            prompt_image_paths = json_data.get(prefix, {}).get("img_paths", [])
            if not prompt_image_paths:
                print(f"[WARNING] No img_paths for {prefix}")
                continue
            
            image_labels = json_data.get(prefix, {}).get("class_label", [])

            # Revert to 32 frames to test if Flash Attention 2 can handle the memory load
            frames = sample_video_frames(video_path, num_frames=32)

            # gme_I_scores = []
            all_prompt_images = []
            all_image_labels = []
            all_local_images = []
            all_yolo_world_conf = []

            frame_obj = 0

            for frame in frames:
                frame_flag = True
                for prompt_image_path, image_label in zip(
                    prompt_image_paths, image_labels
                ):
                    if "face" in prefix and (
                        image_label == "Man" or image_label == "Woman"
                    ):
                        continue

                    if "human" in prefix and (
                        image_label == "Man" or image_label == "Woman"
                    ):
                        image_label = "human"

                    prompt_image_file_path = os.path.join(
                        input_image_folder, prompt_image_path
                    )
                    prompt_image = Image.open(prompt_image_file_path)

                    pred_instances = yoloworld_inference(
                        runner,
                        yolo_vision_model,
                        yolo_processor,
                        txt_feats,
                        frame,
                        prompt_image,
                        device=device # Pass the cpu device
                    )
                    bboxes = pred_instances["bboxes"]
                    confidences = pred_instances["scores"]
                    all_yolo_world_conf.extend(confidences)

                    if len(bboxes) != 0 and frame_flag:
                        frame_obj += 1
                        frame_flag = False

                    for bbox in bboxes:
                        x1, y1, x2, y2 = bbox
                        local_image = frame.crop((x1, y1, x2, y2))
                        all_local_images.append(local_image)
                        all_prompt_images.append(prompt_image)
                        all_image_labels.append(image_label)

            e_main_image_corpus = gme.get_image_embeddings(
                images=all_prompt_images, is_query=False, show_progress_bar=False
            )
            e_query = gme.get_text_embeddings(
                texts=all_image_labels,
                instruction="Find an image that matches the given text.",
                show_progress_bar=False,
            )
            e_local_image_corpus = gme.get_image_embeddings(
                images=all_local_images, is_query=False, show_progress_bar=False
            )

            gme_image_score = (e_main_image_corpus * e_local_image_corpus).sum(-1)
            gme_text_score = (e_query * e_local_image_corpus).sum(-1)

            # DEBUG: Print score stats
            if len(all_yolo_world_conf) > 0:
                print(f"[DEBUG] {prefix}: Found {len(all_yolo_world_conf)} boxes.")
                for i, (b_conf, t_conf, i_score, label) in enumerate(zip(all_yolo_world_conf, gme_text_score, gme_image_score, all_image_labels)):
                    # Lowered text_conf threshold to 0.10 to accommodate generic "*object" labels
                    pass_filter = (b_conf > 0.6 and t_conf > 0.10 and i_score != 0)
                    print(f"  Box {i} [{label}]: bbox={b_conf:.4f}, text={t_conf.item():.4f}, img={i_score.item():.4f} -> {'PASS' if pass_filter else 'FAIL'}")
            else:
                print(f"[DEBUG] {prefix}: No boxes detected by YOLO.")

            retrieval_score_list = []
            for bbox_conf, text_conf, nexus_score in zip(
                all_yolo_world_conf, gme_text_score, gme_image_score
            ):
                if bbox_conf > 0.6 and text_conf > 0.10 and nexus_score != 0:
                    retrieval_score_list.append(nexus_score)

            if len(retrieval_score_list) != 0:
                nexus_score = (
                    torch.mean(torch.tensor(retrieval_score_list)).item() / frame_obj
                )
                # Custom Logic: Sum / (Frames * NumRefs)
                num_refs = len(prompt_image_paths)
                nexus_score_custom = (
                    torch.sum(torch.tensor(retrieval_score_list)).item() / (frame_obj * num_refs)
                )
            else:
                nexus_score = 0
                nexus_score_custom = 0

            results[prefix] = {
                "nexus_score": nexus_score,
                "nexus_score_custom": nexus_score_custom,
            }

        except Exception as e:
            print(f"[ERROR] Failed to process {video_file}: {e}")
            continue

    with open(output_json_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"All results have been saved to {output_json_file}")


if __name__ == "__main__":
    main()
