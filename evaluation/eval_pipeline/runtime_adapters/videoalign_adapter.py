from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import cv2
import pandas as pd
import torch
from tqdm import tqdm


def get_video_fps(video_path: str) -> float | None:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    return fps if fps and fps > 0 else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--videoalign_root", required=True)
    parser.add_argument("--checkpoint_dir", required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--batch_size", type=int, default=1)
    args = parser.parse_args()

    root = Path(args.videoalign_root).resolve()
    checkpoint_dir = Path(args.checkpoint_dir).resolve()
    if not checkpoint_dir.exists():
        raise FileNotFoundError(f"VideoAlign checkpoint_dir does not exist: {checkpoint_dir}")
    if not (checkpoint_dir / "model_config.json").exists():
        raise FileNotFoundError(f"Missing VideoAlign model_config.json in {checkpoint_dir}")
    if not list(checkpoint_dir.glob("checkpoint-*")):
        raise FileNotFoundError(f"Missing VideoAlign checkpoint-* under {checkpoint_dir}")

    sys.path.insert(0, str(root))
    original_cwd = os.getcwd()
    os.chdir(root)
    try:
        from inference import VideoVLMRewardInference

        inferencer = VideoVLMRewardInference(
            load_from_pretrained=str(checkpoint_dir),
            device=args.device,
            dtype=torch.bfloat16,
        )
        df = pd.read_csv(args.input_csv)
        results = []
        with torch.no_grad():
            for start in tqdm(range(0, len(df), args.batch_size), desc="VideoAlign"):
                batch = df.iloc[start : start + args.batch_size]
                videos = batch["video_path"].tolist()
                prompts = batch["text"].tolist()
                rewards = inferencer.reward(
                    videos,
                    prompts,
                    fps=get_video_fps(videos[0]),
                    use_norm=True,
                )
                results.extend(rewards)
        out = pd.concat([df, pd.DataFrame(results)], axis=1)
        out[["video_path", "TA", "VQ", "MQ"]].to_csv(args.output_csv, index=False)
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    main()
