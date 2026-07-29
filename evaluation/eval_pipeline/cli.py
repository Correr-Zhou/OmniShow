from __future__ import annotations

import argparse

from .metrics import METRIC_FAMILIES
from .runner import RunOptions, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run clean video generation metrics.")
    parser.add_argument("--dataset_csv", required=True)
    parser.add_argument("--dataset_root", default=None)
    parser.add_argument("--video_dir", required=True)
    parser.add_argument("--output_dir", required=True)
    parser.add_argument("--checkpoint_dir", required=True)
    parser.add_argument("--cache_dir", default=None)
    parser.add_argument("--metrics", nargs="+", choices=METRIC_FAMILIES, default=None)
    parser.add_argument("--col_prompt", default="text_prompt")
    parser.add_argument("--col_pose", default="pose_data")
    parser.add_argument("--col_ref_img", default='["ref_image_object", "ref_image_human"]')
    parser.add_argument("--col_ref_img_class_label", default='["object_label", "*human"]')
    parser.add_argument("--allow_partial", action="store_true")
    parser.add_argument("--dry_run", action="store_true")
    parser.add_argument("--py_vbench", default=None)
    parser.add_argument("--py_opens2v", default=None)
    parser.add_argument("--py_videoalign", default=None)
    parser.add_argument("--py_syncnet", default=None)
    parser.add_argument("--py_pose", default=None)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    output = run_pipeline(RunOptions(**vars(args)))
    print(f"Final report: {output}")


if __name__ == "__main__":
    main()
