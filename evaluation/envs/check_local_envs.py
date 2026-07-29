from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from eval_pipeline.config import ENV_BY_FAMILY, checkpoint_subdir, project_root, resolve_python_paths
from eval_pipeline.metrics import METRIC_FAMILIES

REQUIRED_WEIGHTS = {
    "vbench": [
        "clip_model/ViT-L-14.pt",
        "aesthetic_model/emb_reader",
        "pyiqa_model/musiq_spaq_ckpt-358bb6af.pth",
    ],
    "opens2v": [
        "yolo_world_v2_l_image_prompt_adapter-719a7afb.pth",
        "face_extractor",
        "glint360k_curricular_face_r101_backbone.bin",
    ],
    "videoalign": ["model_config.json"],
    "syncnet": ["syncnet_v2.model", "sfd_face.pth"],
    "pose": ["yolox_l.onnx", "dw-ll_ucoco_384.onnx"],
}

IMPORT_CHECKS = {
    "vbench": "import torch, pandas; import vbench",
    "opens2v": "import torch, pandas, transformers",
    "opens2v_nexus": "import torch, pandas, transformers, mmengine, mmyolo",
    "videoalign": "import torch, pandas, cv2",
    "syncnet": "import torch, pandas, cv2",
    "pose": "import pandas, cv2, onnxruntime",
}


def check_path(path: Path, errors: list[str], label: str) -> None:
    if not path.exists():
        errors.append(f"Missing {label}: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metrics", nargs="+", choices=METRIC_FAMILIES, default=METRIC_FAMILIES)
    parser.add_argument("--checkpoint_dir", required=True)
    parser.add_argument("--check_imports", action="store_true")
    parser.add_argument("--require_weights", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    python_paths = resolve_python_paths({})
    root = project_root()
    for family in args.metrics:
        vendor_name = {
            "vbench": "VBench",
            "opens2v": "OpenS2V-Nexus",
            "videoalign": "VideoAlign",
            "syncnet": "syncnet_python",
            "pose": "pose_custom",
        }[family]
        check_path(root / "vendor" / vendor_name, errors, f"{family} vendor")
        python_path = Path(python_paths[family])
        if not python_path.exists():
            errors.append(
                f"{ENV_BY_FAMILY[family]} is not an existing Python executable: {python_path}"
            )
        if args.check_imports and python_path.exists():
            result = subprocess.run(
                [str(python_path), "-c", IMPORT_CHECKS[family]],
                text=True,
                capture_output=True,
            )
            if result.returncode != 0:
                errors.append(f"{family} import check failed: {result.stderr.strip()}")
            if family == "opens2v":
                nexus_python = Path(os.environ.get("EVAL_PY_OPENS2V_NEXUS", str(python_path)))
                if not nexus_python.exists():
                    errors.append(
                        f"EVAL_PY_OPENS2V_NEXUS is not an existing Python executable: {nexus_python}"
                    )
                else:
                    result = subprocess.run(
                        [str(nexus_python), "-c", IMPORT_CHECKS["opens2v_nexus"]],
                        text=True,
                        capture_output=True,
                    )
                    if result.returncode != 0:
                        errors.append(
                            f"opens2v nexus import check failed: {result.stderr.strip()}"
                        )
        if args.require_weights:
            family_ckpt = checkpoint_subdir(args.checkpoint_dir, family)
            for rel in REQUIRED_WEIGHTS[family]:
                check_path(family_ckpt / rel, errors, f"{family} weight {rel}")
            if family == "videoalign":
                if not list(family_ckpt.glob("checkpoint-*")):
                    errors.append(f"Missing VideoAlign checkpoint-* under {family_ckpt}")
    if "syncnet" in args.metrics and shutil.which("ffmpeg") is None:
        errors.append("ffmpeg is required for SyncNet but was not found in PATH")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
    print("Environment checks passed.")


if __name__ == "__main__":
    main()
