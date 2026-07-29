"""Pipeline orchestration."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .adapters.opens2v import run_opens2v
from .adapters.pose import run_pose
from .adapters.syncnet import run_syncnet
from .adapters.vbench import run_vbench
from .adapters.videoalign import run_videoalign
from .config import checkpoint_subdir, resolve_python_paths
from .metrics import METRIC_FAMILIES
from .paths import ensure_dirs, load_inputs, resolve_metadata_paths
from .report import FinalReport


@dataclass
class RunOptions:
    dataset_csv: str
    video_dir: str
    output_dir: str
    checkpoint_dir: str
    cache_dir: str | None = None
    dataset_root: str | None = None
    metrics: list[str] | None = None
    col_prompt: str = "text_prompt"
    col_pose: str = "pose_data"
    col_ref_img: str = '["ref_image_object", "ref_image_human"]'
    col_ref_img_class_label: str = '["object_label", "*human"]'
    allow_partial: bool = False
    dry_run: bool = False
    py_vbench: str | None = None
    py_opens2v: str | None = None
    py_videoalign: str | None = None
    py_syncnet: str | None = None
    py_pose: str | None = None


def selected_metrics(metrics: list[str] | None) -> list[str]:
    if not metrics:
        return list(METRIC_FAMILIES)
    normalized = [metric.lower() for metric in metrics]
    unknown = sorted(set(normalized) - set(METRIC_FAMILIES))
    if unknown:
        raise ValueError(f"Unknown metric families: {', '.join(unknown)}")
    return normalized


def run_pipeline(options: RunOptions) -> Path:
    output_dir = Path(options.output_dir)
    checkpoint_dir = Path(options.checkpoint_dir)
    cache_dir = Path(options.cache_dir) if options.cache_dir else None
    families = selected_metrics(options.metrics)
    ensure_dirs([output_dir, output_dir / "logs"])
    for family in families:
        ensure_dirs([output_dir / f"{family}_workspace"])
    metadata, video_paths = load_inputs(
        options.dataset_csv,
        options.video_dir,
        allow_partial=options.allow_partial,
    )
    metadata = resolve_metadata_paths(
        metadata,
        options.dataset_root,
        options.col_pose,
        options.col_ref_img,
    )

    python_paths = resolve_python_paths(
        {
            "vbench": options.py_vbench,
            "opens2v": options.py_opens2v,
            "videoalign": options.py_videoalign,
            "syncnet": options.py_syncnet,
            "pose": options.py_pose,
        }
    )
    config = asdict(options)
    config["resolved_python_paths"] = python_paths
    config["selected_metrics"] = families
    config["video_count"] = len(video_paths)
    (output_dir / "run_config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    report = FinalReport(metadata, video_paths)
    if "videoalign" in families:
        report.merge_raw_metrics(
            run_videoalign(
                metadata,
                video_paths,
                output_dir / "videoalign_workspace",
                python_paths["videoalign"],
                checkpoint_subdir(checkpoint_dir, "videoalign"),
                cache_dir,
                options.col_prompt,
                options.dry_run,
            )
        )
    if "opens2v" in families:
        report.merge_raw_metrics(
            run_opens2v(
                metadata,
                video_paths,
                output_dir / "opens2v_workspace",
                python_paths["opens2v"],
                checkpoint_subdir(checkpoint_dir, "opens2v"),
                cache_dir,
                options.col_ref_img,
                options.col_ref_img_class_label,
                options.dry_run,
                options.allow_partial,
            )
        )
    if "syncnet" in families:
        report.merge_raw_metrics(
            run_syncnet(
                video_paths,
                output_dir / "syncnet_workspace",
                python_paths["syncnet"],
                checkpoint_subdir(checkpoint_dir, "syncnet"),
                cache_dir,
                options.dry_run,
            )
        )
    if "pose" in families:
        report.merge_raw_metrics(
            run_pose(
                metadata,
                video_paths,
                output_dir / "pose_workspace",
                python_paths["pose"],
                checkpoint_subdir(checkpoint_dir, "pose"),
                cache_dir,
                options.col_pose,
                options.dry_run,
            )
        )
    if "vbench" in families:
        report.merge_raw_metrics(
            run_vbench(
                metadata,
                video_paths,
                output_dir / "vbench_workspace",
                python_paths["vbench"],
                checkpoint_subdir(checkpoint_dir, "vbench"),
                cache_dir,
                options.col_prompt,
                options.dry_run,
            )
        )

    return report.write(output_dir / "final_report.csv")
