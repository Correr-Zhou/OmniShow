# Evaluation Code of HOIVG-Bench

## 📖 Introduction

This folder provides the evaluation pipeline used for **HOIVG-Bench**. It
runs selected video generation metrics through a unified CSV-driven entry point,
keeps evaluator-specific dependencies in separate Conda environments, and
merges the results into a single `final_report.csv`.

The implementation is organized as a lightweight orchestration layer around
vendored metric projects:

```text
                              HOIVG-Bench metadata CSV
                                          +
                                  generated videos
                                          |
                                          v
                                  eval_pipeline.cli
                                          |
 +--------------+ +--------------+ +--------------+ +--------------+ +--------------+
 |  VideoAlign  | |   OpenS2V    | |   SyncNet    | |     Pose     | |    VBench    |
 | TA / VQ / MQ | | FaceSim /    | | Sync-C /     | |  AKD / PCK   | |  AES / IQA   |
 |              | | NexusScore   | | Sync-D       | |              | |              |
 +--------------+ +--------------+ +--------------+ +--------------+ +--------------+
        |                |                |                |                |
        +----------------+----------------+----------------+----------------+
                                          |
                                          v
                                    ResultsMerger
                                          |
                                          v
                         merged per-video final_report.csv
```

The released pipeline reports the following metrics:

| Metric | Source | Description |
| :--- | :--- | :--- |
| `TA` | VideoAlign | Text-video alignment. |
| `FaceSim` | OpenS2V-Nexus | Human identity consistency. |
| `NexusScore` | OpenS2V-Nexus | Subject-level consistency. |
| `Sync-C` | SyncNet | Audio-visual synchronization confidence. |
| `Sync-D` | SyncNet | Audio-visual synchronization distance. |
| `AKD` | Pose | Average keypoint distance. |
| `PCK` | Pose | Percentage of correct keypoints. |
| `AES` | VBench | Aesthetic quality. |
| `IQA` | VBench | Imaging quality. |
| `VQ` | VideoAlign | Visual quality. |
| `MQ` | VideoAlign | Motion quality. |

Metrics not listed above may exist in the vendored projects, but they are not
called by this evaluation entry.


## 🛠️ Environment Setup

All commands below should be run from this folder:

```bash
cd /path/to/OmniShow/evaluation
```

This evaluation code uses separate environments because VBench, OpenS2V-Nexus,
VideoAlign, SyncNet, and the pose evaluator have different dependency stacks.
Please install the following environments by following the corresponding
upstream repositories:

| Evaluator | Environment owner |
| :--- | :--- |
| VBench | Follow [VBench](https://github.com/Vchitect/VBench). |
| OpenS2V-Nexus | Follow [OpenS2V-Nexus](https://github.com/PKU-YuanGroup/OpenS2V-Nexus). |
| VideoAlign | Follow [VideoAlign](https://github.com/KwaiVGI/VideoAlign). |
| SyncNet | Follow [SyncNet](https://github.com/joonson/syncnet_python). |
| Pose | Use the environment file in this folder. |

For the pose evaluator, create the environment with:

```bash
conda env create -f envs/pose.yml
```

Edit `envs/local_env.sh` and set the Python executable of each evaluator:

```bash
export EVAL_PY_VBENCH=/path/to/vbench_env/bin/python
export EVAL_PY_OPENS2V=/path/to/opens2v_env/bin/python
export EVAL_PY_OPENS2V_NEXUS=/path/to/opens2v_yoloworld_env/bin/python
export EVAL_PY_VIDEOALIGN=/path/to/videoalign_env/bin/python
export EVAL_PY_SYNCNET=/path/to/syncnet_env/bin/python
export EVAL_PY_POSE=/path/to/pose-eval/bin/python
```

`EVAL_PY_OPENS2V_NEXUS` is optional. Set it only when NexusScore needs a
different OpenS2V/YOLOWorld environment from FaceSim.


## 📦 Checkpoint Preparation

Weights are not included in this release. Please download the required weights
from the corresponding upstream repositories or model pages.

For easier management across multiple evaluators, this evaluation wrapper uses
one checkpoint root with one subdirectory per evaluator:

```text
checkpoints/
├── vbench/
│   ├── clip_model/ViT-L-14.pt
│   ├── aesthetic_model/emb_reader/...
│   └── pyiqa_model/musiq_spaq_ckpt-358bb6af.pth
├── opens2v/
│   ├── yolo_world_v2_l_image_prompt_adapter-719a7afb.pth
│   ├── face_extractor/
│   └── glint360k_curricular_face_r101_backbone.bin
├── videoalign/
│   ├── model_config.json
│   └── checkpoint-*/model.pth
│       # or checkpoint-*/adapter_model.safetensors plus non_lora_state_dict.pth
├── syncnet/
│   ├── syncnet_v2.model
│   └── sfd_face.pth
└── pose/
    ├── yolox_l.onnx
    └── dw-ll_ucoco_384.onnx
```

Pass this parent directory with `--checkpoint_dir`. The adapters map this clean
layout back to the file paths expected by each evaluator.

For NexusScore, `opens2v/` stores the local YOLOWorld checkpoint. The CLIP and
GME models, `openai/clip-vit-base-patch32` and
`Alibaba-NLP/gme-Qwen2-VL-7B-Instruct`, are loaded through the OpenS2V
environment and Hugging Face cache.

Use `--cache_dir` to control runtime caches. If `HF_HOME`, `TORCH_HOME`, or
`XDG_CACHE_HOME` is already exported, the pipeline will keep the existing
setting.


## 📊 HOIVG-Bench Input Format

The evaluation entry is CSV-driven. It reads the benchmark metadata CSV from
[HOIVG-Bench](https://huggingface.co/datasets/donghao-zhou/HOIVG-Bench),
natural-sorts generated videos in `--video_dir`, and aligns CSV rows with video
files by index. The number of CSV rows and generated videos should match.
When `--dataset_root` is set, relative media paths in the CSV are resolved
against that dataset root before evaluator adapters are launched.

The default HOIVG-Bench fields are:

| Field | Description |
| :--- | :--- |
| `text_prompt` | Text prompt used by text-video metrics. |
| `ref_image_human` | Human reference image. |
| `ref_image_object` | Object reference image. |
| `object_label` | Object class label used by OpenS2V-Nexus. |
| `audio` | Reference audio path from HOIVG-Bench. |
| `audio_caption` | Caption for the reference audio. |
| `pose_video` | Reference pose video path from HOIVG-Bench. |
| `pose_data` | Ground-truth pose keypoint data used by AKD/PCK. |

The default OpenS2V reference image and label mapping is:

```text
reference images: ["ref_image_object", "ref_image_human"]
reference labels: ["object_label", "*human"]
```

Values prefixed with `*` are treated as constants. Other values are interpreted
as CSV column names. Use `--col_prompt`, `--col_pose`, `--col_ref_img`, and
`--col_ref_img_class_label` to evaluate a custom CSV layout.


## 🚀 Usage

Prepare the evaluator Python paths:

```bash
cd /path/to/OmniShow/evaluation
source envs/local_env.sh
```

Before launching a long evaluation, run a lightweight preflight check:

```bash
python envs/check_local_envs.py \
  --metrics videoalign opens2v syncnet pose vbench \
  --checkpoint_dir /path/to/checkpoints \
  --check_imports \
  --require_weights
```

This checks Python paths, lightweight imports, required weight files, and
`ffmpeg`. It is not a full GPU runtime test.

To check input paths and configuration without running metric models:

```bash
python -m eval_pipeline.cli \
  --dataset_csv /path/to/HOIVG-Bench/meta_data.csv \
  --dataset_root /path/to/HOIVG-Bench \
  --video_dir /path/to/generated_videos \
  --output_dir /tmp/hoivg_eval_dry_run \
  --checkpoint_dir /path/to/checkpoints \
  --cache_dir /path/to/cache \
  --dry_run
```

Run all released metrics:

```bash
python -m eval_pipeline.cli \
  --dataset_csv /path/to/HOIVG-Bench/meta_data.csv \
  --dataset_root /path/to/HOIVG-Bench \
  --video_dir /path/to/generated_videos \
  --output_dir /path/to/eval_outputs/run_001 \
  --checkpoint_dir /path/to/checkpoints \
  --cache_dir /path/to/cache \
  --metrics videoalign opens2v syncnet pose vbench
```

The output file is:

```text
/path/to/eval_outputs/run_001/final_report.csv
```

The report keeps the input metadata columns, appends `video_path` and
`video_filename`, writes the released metric columns in the table order above,
and adds an `AVERAGE` row for numeric metrics.

Run a subset of metric families with `--metrics`:

```bash
python -m eval_pipeline.cli \
  --dataset_csv /path/to/meta.csv \
  --video_dir /path/to/generated_videos \
  --output_dir /path/to/eval_outputs/opens2v_only \
  --checkpoint_dir /path/to/checkpoints \
  --cache_dir /path/to/cache \
  --metrics opens2v
```

The most commonly edited arguments are:

| Argument | Description |
| :--- | :--- |
| `--dataset_csv` | Metadata CSV for HOIVG-Bench or a compatible dataset. |
| `--dataset_root` | Optional root used to resolve relative media paths. |
| `--video_dir` | Directory containing generated videos. |
| `--output_dir` | Directory where metric workspaces and `final_report.csv` are written. |
| `--checkpoint_dir` | Parent directory of the checkpoint layout above. |
| `--cache_dir` | Cache root for Hugging Face, PyTorch, and related assets. |
| `--metrics` | Metric families to run: `videoalign`, `opens2v`, `syncnet`, `pose`, `vbench`. |
| `--allow_partial` | Optional flag that allows fewer videos than CSV rows. |


## 🗂️ File Structure

```text
evaluation/
├── eval_pipeline/              # CSV loading, metric dispatch, adapters, and report merging.
├── envs/
│   ├── pose.yml                # Maintained Conda environment for the pose evaluator.
│   ├── local_env.sh            # Editable evaluator Python paths for this machine.
│   └── check_local_envs.py     # Lightweight environment and checkpoint preflight.
├── vendor/                     # Vendored evaluator source snapshots.
│   ├── VBench/
│   ├── OpenS2V-Nexus/
│   ├── VideoAlign/
│   ├── syncnet_python/
│   ├── pose_custom/
│   └── NOTICE.md               # License and distribution notice for vendored code.
└── README.md
```

Each directory under `vendor/` contains a `VENDOR.md` file with upstream source,
commit or snapshot information, license, and copy policy. Weights, caches,
generated outputs, and sample media are not included.


## 🧩 Troubleshooting

- CUDA errors usually mean the selected `EVAL_PY_*` environment does not match
  the evaluator's upstream requirements.
- If OpenS2V NexusScore fails, check YOLOWorld/MMEngine/MMCV dependencies and
  the local YOLOWorld checkpoint.
- If NexusScore fails while loading CLIP or GME, check Hugging Face access and
  cache settings for `openai/clip-vit-base-patch32` and
  `Alibaba-NLP/gme-Qwen2-VL-7B-Instruct`.
- If SyncNet fails, check `ffmpeg`, `syncnet_v2.model`, and `sfd_face.pth`.
- If Pose fails, check `onnxruntime-gpu` and the two DWPose ONNX files.
- If row counts differ, fix the generated video directory or use
  `--allow_partial` only while debugging path issues.


## 🤝 Acknowledgements

This evaluation code builds on the excellent open-source projects
[VBench](https://github.com/Vchitect/VBench),
[OpenS2V-Nexus](https://github.com/PKU-YuanGroup/OpenS2V-Nexus),
[VideoAlign](https://github.com/KwaiVGI/VideoAlign),
[SyncNet](https://github.com/joonson/syncnet_python), and
[DWPose](https://github.com/idea-research/dwpose). We sincerely thank the
contributors of these projects and ask users to follow their licenses and model
usage terms.
