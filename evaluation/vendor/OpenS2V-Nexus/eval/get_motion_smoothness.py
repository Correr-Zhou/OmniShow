import os
import json
import argparse
import numpy as np
from PIL import Image
from typing import List
from tqdm import tqdm

import torch.nn as nn
import torch

from q_align.model.builder import load_pretrained_model
from q_align.constants import IMAGE_TOKEN_INDEX
from q_align.mm_utils import tokenizer_image_token

from decord import VideoReader


class QAlignVideoScorer(nn.Module):
    def __init__(self, pretrained="q-future/one-align", device="cuda:0"):
        super().__init__()
        tokenizer, model, image_processor, _ = load_pretrained_model(
            pretrained, None, "mplug_owl2", device=device
        )
        model.to(device)
        model.eval()
        model.requires_grad_(False)
        prompt = "USER: How would you rate the quality of this video?\n<|image|>\nASSISTANT: The quality of the video is"

        self.preferential_ids_ = [
            id_[1]
            for id_ in tokenizer(["excellent", "good", "fair", "poor", "bad"])[
                "input_ids"
            ]
        ]
        self.weight_tensor = (
            torch.Tensor([1, 0.75, 0.5, 0.25, 0.0]).half().to(model.device)
        )

        self.tokenizer = tokenizer
        self.model = model
        self.image_processor = image_processor
        self.input_ids = (
            tokenizer_image_token(
                prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt"
            )
            .unsqueeze(0)
            .to(model.device)
        )

    def expand2square(self, pil_img, background_color):
        width, height = pil_img.size
        if width == height:
            return pil_img
        elif width > height:
            result = Image.new(pil_img.mode, (width, width), background_color)
            result.paste(pil_img, (0, (width - height) // 2))
            return result
        else:
            result = Image.new(pil_img.mode, (height, height), background_color)
            result.paste(pil_img, ((height - width) // 2, 0))
            return result

    def forward(self, video: List[List[Image.Image]], batch_size: int = 64):
        video = [
            [
                self.expand2square(
                    frame, tuple(int(x * 255) for x in self.image_processor.image_mean)
                )
                for frame in vid
            ]
            for vid in video
        ]

        logits_list = []
        softmax_list = []
        weighted_list = []

        with torch.inference_mode():
            for i in range(0, len(video), batch_size):
                batch_videos = video[i : i + batch_size]
                video_tensors = [
                    self.image_processor.preprocess(vid, return_tensors="pt")[
                        "pixel_values"
                    ]
                    .half()
                    .to(self.model.device)
                    for vid in batch_videos
                ]
                input_tensors = self.input_ids.repeat(len(video_tensors), 1)
                output = self.model(input_tensors, images=video_tensors)
                output_logits = output["logits"][:, -1, self.preferential_ids_]
                softmax_logits = torch.softmax(output_logits, -1)
                weighted_scores = softmax_logits @ self.weight_tensor

                logits_list.append(output_logits)
                softmax_list.append(softmax_logits)
                weighted_list.append(weighted_scores)

        final_logits = torch.cat(logits_list, dim=0)
        final_softmax = torch.cat(softmax_list, dim=0)
        final_weighted = torch.cat(weighted_list, dim=0)

        return final_logits, final_softmax, final_weighted


# Read video in sliding window manner, splitting video into segments with number of frames as window_size
def load_video_sliding_window(video_file, window_size=5):
    vr = VideoReader(video_file)
    total_frames = len(vr)
    frames_by_group = []

    # Calculate the left and right extension of the window
    left_extend = (window_size - 1) // 2
    right_extend = window_size - 1 - left_extend

    for current_frame in range(total_frames):
        # Calculate the start and end frame of the window
        start_frame = max(0, current_frame - left_extend)
        end_frame = min(total_frames, current_frame + right_extend + 1)

        frame_indices = list(range(start_frame, end_frame))

        # If there are not enough frames, pad frames on both ends
        while len(frame_indices) < window_size:
            if start_frame == 0:
                frame_indices.append(frame_indices[-1])
            else:
                frame_indices.insert(0, frame_indices[0])

        frames = vr.get_batch(frame_indices).asnumpy()

        # Special handling for the beginning frames to ensure consistency with window_size frames
        if current_frame < left_extend:
            frames_by_group.append([Image.fromarray(frames[0])] * window_size)
        else:
            frames_by_group.append([Image.fromarray(frame) for frame in frames])

    return frames_by_group


# Get frames with poor quality artifacts based on score differences
def get_artifacts_frames(scores, threshold=0.025):
    # Calculate score differences between adjacent frames
    score_diffs = np.abs(np.diff(scores))

    # Identify frames where score differences exceed the threshold
    artifact_indices = np.where(score_diffs > threshold)[0]

    # Return both the current frame and the next frame as significant score difference may be caused by either
    artifacts_frames = np.unique(
        np.concatenate([artifact_indices, artifact_indices + 1])
    )

    return artifacts_frames


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
        "--model_path",
        type=str,
        default="q-future/one-align",
    )
    parser.add_argument("--window_size", type=int, default=3)
    return parser.parse_args()


def main():
    args = parse_args()
    device = "cuda:0"

    input_video_folder = args.input_video_folder
    output_json_folder = args.output_json_folder
    model_path = args.model_path
    window_size = args.window_size

    output_json_file = os.path.join(output_json_folder, "motion_smoothness.json")
    os.makedirs(output_json_folder, exist_ok=True)
    if os.path.exists(output_json_file):
        print("continue")
        return

    scorer = QAlignVideoScorer(pretrained=model_path, device=device)
    print("load model successfully")

    video_files = [f for f in os.listdir(input_video_folder) if f.endswith(".mp4")]

    results_dict = {}
    for video_filename in tqdm(video_files, desc="Processing videos"):
        video_name = os.path.splitext(video_filename)[0]
        _, _, scores = scorer(
            load_video_sliding_window(
                os.path.join(input_video_folder, video_filename), window_size
            )
        )
        scores = scores.tolist()
        artifacts_frames = get_artifacts_frames(scores)
        final_score = 1 - len(artifacts_frames) / len(scores)
        results_dict[video_name] = {"motion_smoothness": final_score}

    with open(output_json_file, "w") as results_file:
        json.dump(results_dict, results_file, indent=4)

    print(f"All results have been saved to {output_json_file}")


if __name__ == "__main__":
    main()
