"""Shared adapter helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run_command(
    cmd: list[str],
    cwd: str | Path | None = None,
    env: dict[str, str] | None = None,
    dry_run: bool = False,
) -> None:
    print("[clean-eval]", " ".join(str(part) for part in cmd))
    if dry_run:
        return
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    subprocess.run(cmd, cwd=cwd, env=merged_env, check=True)


def write_adapter_input(rows, output_csv: Path) -> Path:
    import pandas as pd

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_csv, index=False)
    return output_csv
