"""Runtime configuration helpers."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from .metrics import METRIC_FAMILIES

ENV_BY_FAMILY = {
    "vbench": "EVAL_PY_VBENCH",
    "opens2v": "EVAL_PY_OPENS2V",
    "videoalign": "EVAL_PY_VIDEOALIGN",
    "syncnet": "EVAL_PY_SYNCNET",
    "pose": "EVAL_PY_POSE",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_python_paths(cli_values: dict[str, str | None] | None = None) -> dict[str, str]:
    cli_values = cli_values or {}
    resolved = {}
    for family in METRIC_FAMILIES:
        cli_value = cli_values.get(family)
        if cli_value:
            resolved[family] = cli_value
            continue
        env_value = os.environ.get(ENV_BY_FAMILY[family])
        resolved[family] = env_value or sys.executable
    return resolved


def cache_env(cache_dir: str | Path | None) -> dict[str, str]:
    if not cache_dir:
        return {}
    root = Path(cache_dir)
    defaults = {
        "HF_HOME": root / "huggingface",
        "TORCH_HOME": root / "torch",
        "XDG_CACHE_HOME": root,
    }
    return {key: str(value) for key, value in defaults.items() if not os.environ.get(key)}


def checkpoint_subdir(checkpoint_dir: str | Path, family: str) -> Path:
    return Path(checkpoint_dir) / family
