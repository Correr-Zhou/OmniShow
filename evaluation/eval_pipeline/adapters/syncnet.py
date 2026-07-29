"""SyncNet Sync-C/Sync-D adapter."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import cache_env, project_root
from .common import run_command, write_adapter_input


def run_syncnet(
    video_paths: list[Path],
    workspace: Path,
    python_path: str,
    checkpoint_dir: Path,
    cache_dir: Path | None,
    dry_run: bool = False,
) -> pd.DataFrame:
    input_csv = write_adapter_input(
        [{"video_path": str(path)} for path in video_paths],
        workspace / "syncnet_input.csv",
    )
    output_csv = workspace / "syncnet_results.csv"
    adapter = project_root() / "eval_pipeline" / "runtime_adapters" / "syncnet_adapter.py"
    run_command(
        [
            python_path,
            str(adapter),
            "--input_csv",
            str(input_csv),
            "--output_csv",
            str(output_csv),
            "--syncnet_root",
            str(project_root() / "vendor" / "syncnet_python"),
            "--model_path",
            str(checkpoint_dir / "syncnet_v2.model"),
            "--tmp_dir",
            str(workspace / "tmp"),
        ],
        env=cache_env(cache_dir),
        dry_run=dry_run,
    )
    if dry_run:
        return pd.DataFrame({"video_filename": [p.name for p in video_paths]})
    df = pd.read_csv(output_csv)
    df["video_filename"] = df["video_path"].map(lambda p: Path(str(p)).name)
    return df[["video_filename", "Sync-C", "Sync-D"]]
