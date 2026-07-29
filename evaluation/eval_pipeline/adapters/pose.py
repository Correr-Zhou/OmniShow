"""Pose AKD/PCK adapter."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import cache_env, project_root
from .common import run_command, write_adapter_input


def normalize_pose_results(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    kept = []
    for row in rows:
        item = {"video_filename": row["video_filename"]}
        if "pose_akd_body" in row:
            item["pose_akd_body"] = row["pose_akd_body"]
        if "pose_pck_body" in row:
            item["pose_pck_body"] = row["pose_pck_body"]
        kept.append(item)
    return kept


def run_pose(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    workspace: Path,
    python_path: str,
    checkpoint_dir: Path,
    cache_dir: Path | None,
    pose_column: str,
    dry_run: bool = False,
) -> pd.DataFrame:
    rows = [
        {"video_path": str(video_paths[idx]), "pose_gt": row[pose_column]}
        for idx, (_, row) in enumerate(metadata.iterrows())
    ]
    input_csv = write_adapter_input(rows, workspace / "pose_input.csv")
    output_csv = workspace / "pose_results.csv"
    adapter = project_root() / "eval_pipeline" / "runtime_adapters" / "pose_adapter.py"
    run_command(
        [
            python_path,
            str(adapter),
            "--input_csv",
            str(input_csv),
            "--output_csv",
            str(output_csv),
            "--pose_root",
            str(project_root() / "vendor" / "pose_custom"),
            "--checkpoint_dir",
            str(checkpoint_dir),
        ],
        env=cache_env(cache_dir),
        dry_run=dry_run,
    )
    if dry_run:
        return pd.DataFrame({"video_filename": [p.name for p in video_paths]})
    df = pd.read_csv(output_csv)
    rows = normalize_pose_results(df.to_dict(orient="records"))
    return pd.DataFrame(rows)
