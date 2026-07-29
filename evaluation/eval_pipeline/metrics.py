"""Metric names retained by the clean evaluation pipeline."""

METRIC_COLUMNS = [
    "TA",
    "FaceSim",
    "NexusScore",
    "Sync-C",
    "Sync-D",
    "AKD",
    "PCK",
    "AES",
    "IQA",
    "VQ",
    "MQ",
]

RAW_TO_FINAL = {
    "TA": "TA",
    "opens2v_facesim": "FaceSim",
    "opens2v_nexus": "NexusScore",
    "Sync-C": "Sync-C",
    "Sync-D": "Sync-D",
    "pose_akd_body": "AKD",
    "pose_pck_body": "PCK",
    "vbench_aesthetic_quality": "AES",
    "vbench_imaging_quality": "IQA",
    "VQ": "VQ",
    "MQ": "MQ",
}

FINAL_TO_RAW = {
    "TA": "TA",
    "FaceSim": "opens2v_facesim",
    "NexusScore": "opens2v_nexus",
    "Sync-C": "Sync-C",
    "Sync-D": "Sync-D",
    "AKD": "pose_akd_body",
    "PCK": "pose_pck_body",
    "AES": "vbench_aesthetic_quality",
    "IQA": "vbench_imaging_quality",
    "VQ": "VQ",
    "MQ": "MQ",
}

METRIC_FAMILIES = ["videoalign", "opens2v", "syncnet", "pose", "vbench"]

FAMILY_TO_COLUMNS = {
    "videoalign": ["TA", "VQ", "MQ"],
    "opens2v": ["FaceSim", "NexusScore"],
    "syncnet": ["Sync-C", "Sync-D"],
    "pose": ["AKD", "PCK"],
    "vbench": ["AES", "IQA"],
}
