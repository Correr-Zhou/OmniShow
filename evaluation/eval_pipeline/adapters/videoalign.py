"""VideoAlign TA/VQ/MQ adapter."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import cache_env, project_root
from .common import run_command, write_adapter_input


def run_videoalign(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    workspace: Path,
    python_path: str,
    checkpoint_dir: Path,
    cache_dir: Path | None,
    prompt_column: str,
    dry_run: bool = False,
) -> pd.DataFrame:
    rows = [
        {"video_path": str(video_paths[idx]), "text": row[prompt_column]}
        for idx, (_, row) in enumerate(metadata.iterrows())
    ]
    input_csv = write_adapter_input(rows, workspace / "videoalign_input.csv")
    output_csv = workspace / "videoalign_results.csv"
    adapter = project_root() / "eval_pipeline" / "runtime_adapters" / "videoalign_adapter.py"
    run_command(
        [
            python_path,
            str(adapter),
            "--input_csv",
            str(input_csv),
            "--output_csv",
            str(output_csv),
            "--videoalign_root",
            str(project_root() / "vendor" / "VideoAlign"),
            "--checkpoint_dir",
            str(checkpoint_dir),
        ],
        env=cache_env(cache_dir),
        dry_run=dry_run,
    )
    if dry_run:
        return pd.DataFrame({"video_filename": [p.name for p in video_paths]})
    df = pd.read_csv(output_csv)
    df["video_filename"] = df["video_path"].map(lambda p: Path(str(p)).name)
    return df[["video_filename", "TA", "VQ", "MQ"]]
