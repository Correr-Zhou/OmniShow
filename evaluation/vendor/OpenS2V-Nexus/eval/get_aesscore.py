import os
import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from transformers import (
    CLIPProcessor,
    CLIPVisionModelWithProjection,
)
from tqdm import tqdm
import argparse
import json
import decord


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


@torch.no_grad
def run_aesthetic_laion(model, image):
    if not isinstance(image, list):
        image = [image]
    return model(image)


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(768, 1024),
            nn.Dropout(0.2),
            nn.Linear(1024, 128),
            nn.Dropout(0.2),
            nn.Linear(128, 64),
            nn.Dropout(0.1),
            nn.Linear(64, 16),
            nn.Linear(16, 1),
        )

    @torch.no_grad()
    def forward(self, embed):
        return self.layers(embed)


class AestheticScorer(torch.nn.Module):
    def __init__(self, dtype, aes_clip_path, aes_main_path):
        super().__init__()
        self.clip = CLIPVisionModelWithProjection.from_pretrained(aes_clip_path)
        self.processor = CLIPProcessor.from_pretrained(aes_clip_path)

        self.mlp = MLP()
        state_dict = torch.load(
            aes_main_path, weights_only=True, map_location=torch.device("cpu")
        )
        self.mlp.load_state_dict(state_dict)
        self.dtype = dtype
        self.eval()

    @torch.no_grad()
    def __call__(self, images):
        device = next(self.parameters()).device
        inputs = self.processor(images=images, return_tensors="pt")
        inputs = {k: v.to(self.dtype).to(device) for k, v in inputs.items()}
        embed = self.clip(**inputs)[0]
        # normalize embedding
        embed = embed / torch.linalg.vector_norm(embed, dim=-1, keepdim=True)
        return self.mlp(embed).squeeze(1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_video_folder",
        type=str,
        default="demo_result/model_name_input_video",
    )
    parser.add_argument(
        "--output_json_folder",
        type=str,
        default="demo_result/model_name_output_json",
    )
    parser.add_argument(
        "--aes_clip_path",
        type=str,
        default="openai/clip-vit-large-patch14",
    )
    parser.add_argument(
        "--aes_main_path",
        type=str,
        default="BestWishYsh/OpenS2V-Weight/aesthetic-model.pth",
    )
    parser.add_argument("--num_frames", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()
    device = "cuda"

    input_video_folder = args.input_video_folder
    output_json_folder = args.output_json_folder
    aes_clip_path = args.aes_clip_path
    aes_main_path = args.aes_main_path
    num_frames = args.num_frames

    output_json_file = os.path.join(output_json_folder, "aesthetic_score.json")
    os.makedirs(output_json_folder, exist_ok=True)
    if os.path.exists(output_json_file):
        print("continue")
        return

    aes_model = AestheticScorer(
        dtype=torch.float32, aes_clip_path=aes_clip_path, aes_main_path=aes_main_path
    ).to(device)

    all_results = {}
    for video_filename in tqdm(os.listdir(input_video_folder)):
        video_path = os.path.join(input_video_folder, video_filename)
        if os.path.isfile(video_path) and video_filename.lower().endswith(
            (".mp4", ".mov", ".avi")
        ):
            print(f"Processing video: {video_filename}")
            frames = sample_video_frames(video_path, num_frames=num_frames)
            aes_scores = run_aesthetic_laion(aes_model, frames)
            aes_score = aes_scores.mean().detach().item()
            video_prefix = os.path.splitext(video_filename)[0]
            all_results[video_prefix] = {"aes_score": aes_score}
            print(f"Video: {video_filename}, aes score: {aes_score}")

    with open(output_json_file, "w") as f:
        json.dump(all_results, f, indent=4)

    print(f"All results have been saved to {output_json_file}")


if __name__ == "__main__":
    main()
