"""Final report assembly."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .metrics import METRIC_COLUMNS, RAW_TO_FINAL


class FinalReport:
    def __init__(self, metadata: pd.DataFrame, video_paths: list[Path]):
        if len(metadata) != len(video_paths):
            raise ValueError("metadata and video_paths must have the same length")
        self._metadata_columns = list(metadata.columns)
        self.df = metadata.copy().reset_index(drop=True)
        self.df["video_path"] = [str(path) for path in video_paths]
        self.df["video_filename"] = [path.name for path in video_paths]
        for column in METRIC_COLUMNS:
            self.df[column] = pd.NA

    def merge_raw_metrics(self, metrics_df: pd.DataFrame) -> None:
        if metrics_df.empty:
            return
        if "video_filename" not in metrics_df.columns:
            raise ValueError("metric results must contain video_filename")

        normalized = pd.DataFrame({"video_filename": metrics_df["video_filename"]})
        for raw_name, final_name in RAW_TO_FINAL.items():
            if raw_name in metrics_df.columns:
                normalized[final_name] = metrics_df[raw_name]

        indexed = self.df.set_index("video_filename")
        updates = normalized.set_index("video_filename")
        for column in METRIC_COLUMNS:
            if column in updates.columns:
                indexed.loc[updates.index, column] = updates[column]
        self.df = indexed.reset_index()
        ordered = self._metadata_columns + ["video_path", "video_filename"] + METRIC_COLUMNS
        self.df = self.df[ordered]

    def with_average(self) -> pd.DataFrame:
        ordered = self._metadata_columns + ["video_path", "video_filename"] + METRIC_COLUMNS
        output = self.df[ordered].copy()
        avg_row = {column: pd.NA for column in ordered}
        avg_row["video_filename"] = "AVERAGE"
        for column in METRIC_COLUMNS:
            avg_row[column] = pd.to_numeric(output[column], errors="coerce").mean()
        return pd.concat([output, pd.DataFrame([avg_row])], ignore_index=True)

    def write(self, output_path: str | Path) -> Path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.with_average().to_csv(path, index=False)
        return path
