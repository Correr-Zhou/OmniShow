"""Input path discovery and alignment."""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import pandas as pd

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".gif"}


def natural_key(path: Path) -> list[object]:
    parts = re.split(r"(\d+)", path.name)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def collect_video_paths(video_dir: str | Path) -> list[Path]:
    root = Path(video_dir)
    if not root.exists():
        raise FileNotFoundError(f"Video directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"Video path is not a directory: {root}")
    videos = [
        p
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
    ]
    return sorted(videos, key=natural_key)


def load_inputs(
    dataset_csv: str | Path,
    video_dir: str | Path,
    allow_partial: bool = False,
) -> tuple[pd.DataFrame, list[Path]]:
    csv_path = Path(dataset_csv)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset CSV does not exist: {csv_path}")

    metadata = pd.read_csv(csv_path)
    videos = collect_video_paths(video_dir)
    if len(metadata) != len(videos):
        if not allow_partial:
            raise ValueError(
                "Dataset/video count mismatch: "
                f"{len(metadata)} CSV rows vs {len(videos)} videos. "
                "Use --allow_partial only for debugging."
            )
        keep = min(len(metadata), len(videos))
        metadata = metadata.iloc[:keep].reset_index(drop=True)
        videos = videos[:keep]
    return metadata.reset_index(drop=True), videos


def parse_column_spec(value: str | list[str]) -> list[str]:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            parsed = value
    if isinstance(parsed, list):
        return [str(item) for item in parsed]
    return [str(parsed)]


def is_remote_path(value: str) -> bool:
    return urlparse(value).scheme in {"http", "https", "s3", "gs", "hf"}


def resolve_path_value(value: object, root: Path) -> object:
    if pd.isna(value):
        return value
    text = str(value)
    if not text or is_remote_path(text):
        return value
    path = Path(text)
    if path.is_absolute():
        return str(path)
    return str(root / path)


def resolve_metadata_paths(
    metadata: pd.DataFrame,
    dataset_root: str | Path | None,
    pose_column: str,
    ref_img_columns: str | list[str],
) -> pd.DataFrame:
    if not dataset_root:
        return metadata
    root = Path(dataset_root)
    resolved = metadata.copy()
    columns = [pose_column] + parse_column_spec(ref_img_columns)
    for column in columns:
        if column not in resolved.columns:
            continue
        resolved[column] = resolved[column].map(lambda value: resolve_path_value(value, root))
    return resolved


def ensure_dirs(paths: Iterable[str | Path]) -> None:
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)
