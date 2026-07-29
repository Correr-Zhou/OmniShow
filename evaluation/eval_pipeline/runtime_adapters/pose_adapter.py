from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--pose_root", required=True)
    parser.add_argument("--checkpoint_dir", required=True)
    args = parser.parse_args()

    pose_root = Path(args.pose_root).resolve()
    checkpoint_dir = Path(args.checkpoint_dir).resolve()
    det = checkpoint_dir / "yolox_l.onnx"
    pose = checkpoint_dir / "dw-ll_ucoco_384.onnx"
    if not det.exists():
        raise FileNotFoundError(f"Missing DWPose detector ONNX: {det}")
    if not pose.exists():
        raise FileNotFoundError(f"Missing DWPose pose ONNX: {pose}")

    os.environ["DWPPOSE_DET_ONNX"] = str(det)
    os.environ["DWPPOSE_POSE_ONNX"] = str(pose)
    os.environ["DWPOSE_DET_ONNX"] = str(det)
    os.environ["DWPOSE_POSE_ONNX"] = str(pose)
    sys.path.insert(0, str(pose_root))

    from evaluate_pose import PoseEvaluator

    evaluator = PoseEvaluator()
    if hasattr(evaluator, "load_model"):
        evaluator.load_model()
    df = pd.read_csv(args.input_csv)
    rows = []
    for _, row in df.iterrows():
        if hasattr(evaluator, "evaluate_video"):
            metrics = evaluator.evaluate_video(row["video_path"], row["pose_gt"])
        else:
            metrics = evaluator.evaluate(
                row["video_path"],
                row["pose_gt"],
                sample_stride=8,
                resize_short_edge=720,
            )
        rows.append(
            {
                "video_filename": Path(row["video_path"]).name,
                "pose_akd_body": metrics.get("pose_akd_body", metrics.get("akd_body")),
                "pose_pck_body": metrics.get("pose_pck_body", metrics.get("pck_body")),
            }
        )
    pd.DataFrame(rows).to_csv(args.output_csv, index=False)


if __name__ == "__main__":
    main()
