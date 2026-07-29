"""VBench AES/IQA adapter."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from ..config import cache_env, project_root
from .common import run_command


def write_prompt_file(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    prompt_column: str,
    output_path: Path,
) -> Path:
    payload = {
        video_paths[idx].name: row[prompt_column]
        for idx, (_, row) in enumerate(metadata.iterrows())
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def parse_vbench_results(workspace: Path, video_paths: list[Path]) -> pd.DataFrame:
    rows = {path.name: {"video_filename": path.name} for path in video_paths}
    mapping = {
        "aesthetic_quality": "vbench_aesthetic_quality",
        "imaging_quality": "vbench_imaging_quality",
    }
    timestamped_results = sorted(
        workspace.glob("*_eval_results.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    result_files = timestamped_results or [
        path
        for dimension in mapping
        for path in (
            workspace / dimension / f"{dimension}.json",
            workspace / f"{dimension}_eval_results.json",
        )
        if path.exists()
    ]
    if not result_files:
        raise FileNotFoundError(f"VBench result not found in {workspace}")

    found_dimensions: set[str] = set()
    for result_path in result_files:
        data = json.loads(result_path.read_text(encoding="utf-8"))
        for dimension, column in mapping.items():
            if isinstance(data, dict) and dimension in data:
                content = data[dimension]
                items = content[1] if isinstance(content, list) and len(content) >= 2 else content
            elif isinstance(data, dict):
                items = data.get("video_results", data.get("results", data))
            else:
                items = data
            if isinstance(items, list):
                for item in items:
                    filename = Path(str(item.get("video_path", item.get("video_filename", "")))).name
                    score = item.get("video_results", item.get("score", item.get(dimension)))
                    if filename in rows and score is not None:
                        rows[filename][column] = score
                        found_dimensions.add(dimension)
            elif isinstance(items, dict):
                for filename, value in items.items():
                    name = Path(filename).name
                    if isinstance(value, dict):
                        value = value.get("video_results", value.get("score", value.get(dimension)))
                    if name in rows and value is not None:
                        rows[name][column] = value
                        found_dimensions.add(dimension)
        if found_dimensions == set(mapping):
            break
    missing = set(mapping) - found_dimensions
    if missing:
        raise FileNotFoundError(f"VBench result missing dimensions: {sorted(missing)}")
    return pd.DataFrame(list(rows.values()))


def run_vbench(
    metadata: pd.DataFrame,
    video_paths: list[Path],
    workspace: Path,
    python_path: str,
    checkpoint_dir: Path,
    cache_dir: Path | None,
    prompt_column: str,
    dry_run: bool = False,
) -> pd.DataFrame:
    root = project_root()
    vendor_root = root / "vendor" / "VBench"
    prompt_file = write_prompt_file(
        metadata, video_paths, prompt_column, workspace / "vbench_input.json"
    )
    env = cache_env(cache_dir)
    env["VBENCH_CACHE_DIR"] = str(checkpoint_dir)
    env["NCCL_NET_PLUGIN"] = "none"
    env["PYTHONUNBUFFERED"] = "1"
    videos_dir = str(Path(video_paths[0]).parent) if video_paths else ""
    run_command(
        [
            python_path,
            "-u",
            str(vendor_root / "evaluate.py"),
            "--videos_path",
            videos_dir,
            "--mode",
            "custom_input",
            "--prompt_file",
            str(prompt_file),
            "--dimension",
            "aesthetic_quality",
            "imaging_quality",
            "--output_path",
            str(workspace),
            "--load_ckpt_from_local",
            "True",
        ],
        cwd=vendor_root,
        env=env,
        dry_run=dry_run,
    )
    if dry_run:
        return pd.DataFrame({"video_filename": [p.name for p in video_paths]})
    return parse_vbench_results(workspace, video_paths)
