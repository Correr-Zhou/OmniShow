"""OpenS2V FaceSim and NexusScore adapter."""

from __future__ import annotations

import ast
import json
import os
import subprocess
from pathlib import Path

import pandas as pd

from ..config import cache_env, project_root
from .common import run_command


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


def build_input_json(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    output_path: str | Path,
    ref_img_columns: str | list[str],
    ref_label_columns: str | list[str],
) -> dict[str, dict[str, object]]:
    image_columns = parse_column_spec(ref_img_columns)
    label_columns = parse_column_spec(ref_label_columns)
    if len(image_columns) != len(label_columns):
        raise ValueError("reference image columns and label columns must match")

    payload: dict[str, dict[str, object]] = {}
    if len(metadata) > len(video_paths):
        raise ValueError("metadata rows exceed discovered videos")

    for idx, (_, row) in enumerate(metadata.iterrows()):
        images = []
        labels = []
        for image_column, label_column in zip(image_columns, label_columns):
            images.append(row[image_column])
            if label_column.startswith("*"):
                labels.append(label_column[1:])
            else:
                labels.append(row[label_column])
        payload[video_paths[idx].stem] = {
            "video_path": str(video_paths[idx]),
            "img_paths": images,
            "class_label": labels,
        }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def merge_opens2v_json(json_path: Path, output_column: str, video_paths: list[Path]) -> pd.DataFrame:
    if not json_path.exists():
        raise FileNotFoundError(f"OpenS2V result not found: {json_path}")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    rows = []
    for video_path in video_paths:
        value = data.get(video_path.stem)
        if isinstance(value, dict):
            if output_column == "opens2v_facesim":
                value = value.get("cur_score", value.get("facesim", value.get("score")))
            elif output_column == "opens2v_nexus":
                value = value.get("nexus_score", value.get("nexus", value.get("score")))
        rows.append({"video_filename": video_path.name, output_column: value})
    return pd.DataFrame(rows)


def run_opens2v(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    workspace: Path,
    python_path: str,
    checkpoint_dir: Path,
    cache_dir: Path | None,
    ref_img_columns: str,
    ref_label_columns: str,
    dry_run: bool = False,
    allow_partial: bool = False,
) -> pd.DataFrame:
    root = project_root()
    vendor_root = root / "vendor" / "OpenS2V-Nexus"
    eval_dir = vendor_root / "eval"
    input_json = workspace / "opens2v_input.json"
    build_input_json(metadata, video_paths, input_json, ref_img_columns, ref_label_columns)

    env = cache_env(cache_dir)
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    yolo_path = eval_dir / "utils" / "yoloworld"
    env["PYTHONPATH"] = f"{yolo_path}:{env.get('PYTHONPATH', '')}"

    videos_dir = str(Path(video_paths[0]).parent) if video_paths else ""
    facesim_json = workspace / "facesim.json"
    nexus_json = workspace / "nexusscore.json"

    run_command(
        [
            python_path,
            str(eval_dir / "get_facesim.py"),
            "--input_video_folder",
            videos_dir,
            "--input_json_file",
            str(input_json),
            "--output_json_folder",
            str(workspace),
            "--model_path",
            str(checkpoint_dir),
            "--input_image_folder",
            "",
            "--num_frames",
            "8",
        ],
        cwd=eval_dir,
        env=env,
        dry_run=dry_run,
    )
    nexus_python_path = os.environ.get("EVAL_PY_OPENS2V_NEXUS", python_path)
    try:
        run_command(
            [
                nexus_python_path,
                str(eval_dir / "get_nexusscore.py"),
                "--input_video_folder",
                videos_dir,
                "--input_json_file",
                str(input_json),
                "--output_json_folder",
                str(workspace),
                "--yolo_model_path",
                str(checkpoint_dir / "yolo_world_v2_l_image_prompt_adapter-719a7afb.pth"),
                "--input_image_folder",
                "",
            ],
            cwd=eval_dir,
            env=env,
            dry_run=dry_run,
        )
    except subprocess.CalledProcessError:
        if not allow_partial:
            raise
        print("[clean-eval] OpenS2V NexusScore failed; keeping FaceSim and leaving NexusScore empty.")

    if dry_run:
        return pd.DataFrame({"video_filename": [p.name for p in video_paths]})
    facesim = merge_opens2v_json(facesim_json, "opens2v_facesim", video_paths)
    if nexus_json.exists():
        nexus = merge_opens2v_json(nexus_json, "opens2v_nexus", video_paths)
    else:
        nexus = pd.DataFrame(
            {"video_filename": [p.name for p in video_paths], "opens2v_nexus": [None] * len(video_paths)}
        )
    return facesim.merge(nexus, on="video_filename", how="outer")
