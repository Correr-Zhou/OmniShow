from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


class Options:
    def __init__(self, tmp_dir: str, batch_size: int = 20, vshift: int = 15, reference: str = "demo"):
        self.tmp_dir = tmp_dir
        self.batch_size = batch_size
        self.vshift = vshift
        self.reference = reference


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True)
    parser.add_argument("--output_csv", required=True)
    parser.add_argument("--syncnet_root", required=True)
    parser.add_argument("--model_path", required=True)
    parser.add_argument("--tmp_dir", required=True)
    parser.add_argument("--min_track", type=int, default=10)
    args = parser.parse_args()

    root = Path(args.syncnet_root).resolve()
    model_path = Path(args.model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"SyncNet model not found: {model_path}")
    s3fd_weight = model_path.parent / "sfd_face.pth"
    if not s3fd_weight.exists():
        raise FileNotFoundError(f"SyncNet S3FD face detector weight not found: {s3fd_weight}")
    vendor_s3fd_weight = root / "detectors" / "s3fd" / "weights" / "sfd_face.pth"
    created_s3fd_symlink = False
    if not vendor_s3fd_weight.exists():
        vendor_s3fd_weight.parent.mkdir(parents=True, exist_ok=True)
        vendor_s3fd_weight.symlink_to(s3fd_weight)
        created_s3fd_symlink = True

    sys.path.insert(0, str(root))
    original_cwd = os.getcwd()
    os.chdir(root)
    try:
        from SyncNetInstance import SyncNetInstance

        syncnet = SyncNetInstance()
        syncnet.loadParameters(str(model_path))
        df = pd.read_csv(args.input_csv)
        tmp_dir = Path(args.tmp_dir)
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(parents=True)
        pipeline_script = root / "run_pipeline.py"
        results = []
        for idx, video_path in enumerate(tqdm(df["video_path"].tolist(), desc="SyncNet")):
            ref_name = f"vid_{idx}"
            subprocess.run(
                [
                    sys.executable,
                    str(pipeline_script),
                    "--videofile",
                    video_path,
                    "--reference",
                    ref_name,
                    "--data_dir",
                    str(tmp_dir),
                    "--min_track",
                    str(args.min_track),
                ],
                check=True,
            )
            crop_files = sorted(glob.glob(str(tmp_dir / "pycrop" / ref_name / "*.avi")))
            if not crop_files:
                results.append({"Sync-C": np.nan, "Sync-D": np.nan})
                continue
            distances = []
            confidences = []
            for crop in crop_files:
                offset, confidence, dist = syncnet.evaluate(Options(str(tmp_dir), reference=ref_name), videofile=crop)
                mean_distances = np.mean(np.asarray(dist), axis=0)
                distances.append(float(np.min(mean_distances)))
                confidences.append(float(confidence))
            results.append({"Sync-C": max(confidences), "Sync-D": min(distances)})
        out = pd.concat([df, pd.DataFrame(results)], axis=1)
        out[["video_path", "Sync-C", "Sync-D"]].to_csv(args.output_csv, index=False)
    finally:
        os.chdir(original_cwd)
        if created_s3fd_symlink and vendor_s3fd_weight.is_symlink():
            vendor_s3fd_weight.unlink()


if __name__ == "__main__":
    main()
