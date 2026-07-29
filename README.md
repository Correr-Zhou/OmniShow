<div align="center">
  <img width="320" alt="OmniShow logo" src="assets/logo_cropped.png">
</div>

<h1 align="center" style="line-height: 50px;">
  OmniShow: Unifying Multimodal Conditions for Human-Object Interaction Video Generation
</h1>

<div align="center">
Donghao Zhou<sup>1,*</sup>, Guisheng Liu<sup>2,*</sup>, Hao Yang<sup>2</sup>, Jiatong Li<sup>2,†</sup>, Jingyu Lin<sup>3</sup>, Xiaohu Huang<sup>4</sup>,<br>
Yichen Liu<sup>2</sup>, Xin Gao<sup>2</sup>, Cunjian Chen<sup>3</sup>, Shilei Wen<sup>2,§</sup>, Chi-Wing Fu<sup>1</sup>, Pheng-Ann Heng<sup>1,§</sup>
</div>

<br>

<div align="center">
<sup>1</sup>The Chinese University of Hong Kong, <sup>2</sup>ByteDance, <sup>3</sup>Monash University, <sup>4</sup>The University of Hong Kong
</div>

<br>

<div align="center">
<sup>*</sup>Equal contribution, <sup>†</sup>Project lead, <sup>§</sup>Corresponding author
</div>

<br>

<div align="center">
  <a href="http://correr-zhou.github.io/OmniShow"><img src="https://img.shields.io/static/v1?label=Project%20Page&message=Web&color=green"></a> &ensp;
  <a href="https://arxiv.org/pdf/2604.11804"><img src="https://img.shields.io/static/v1?label=Paper&message=arXiv&color=red"></a> &ensp;
  <a href="https://github.com/Correr-Zhou/OmniShow"><img src="https://img.shields.io/static/v1?label=Code&message=GitHub&color=blue"></a> &ensp;
  <a href="https://huggingface.co/datasets/donghao-zhou/HOIVG-Bench"><img src="https://img.shields.io/static/v1?label=Benchmark&message=HOIVG-Bench&color=yellow"></a> 
</div>

---

## 🔥 Updates

- 2026.07: The evaluation code of HOIVG-Bench is released!
- 2026.05: Training and inference code for Wan-based models is released!
- 2026.05: OmniShow is accepted by ICML 2026! 🎉
- 2026.04: The [Data of HOIVG-Bench](https://huggingface.co/datasets/donghao-zhou/HOIVG-Bench) is available on HuggingFace! 🤗
- 2026.04: The [technical report of OmniShow](https://arxiv.org/pdf/2604.11804) is released!


## 🌟 Highlights
- **Multimodal Controllable Model**: OmniShow is the first all-in-one model for Human-Object Interaction Video Generation (HOIVG) with text, reference image, audio, and pose conditioning.
- **Flexible Task Coverage**: A single model supports R2V, RA2V, RP2V, and RAP2V generation within one coherent framework.
- **Enabling Broader Applications**: OmniShow exhibits remarkable versatility in broader
applications, such as audio-driven avatars, object swapping, and video remixing.
- **New Benchmark**: HOIVG-Bench provides a dedicated and comprehensive benchmark for evaluating HOIVG under diverse multimodal conditions.

<div align="center">
  <img width="1080" alt="OmniShow Overview" src="assets/teaser.png">
</div>

## 🚀 Introducing OmniShow

We propose **OmniShow**, a video generation model that unifies text, reference image, audio, and pose conditions for HOIVG, which consists of:

1. **Unified Channel-wise Conditioning** effectively injects reference image and pose cues via unified channel concatenation. It augments noisy video tokens with pseudo-frames, which are supervised by a reference reconstruction loss to preserve semantic details.
2. **Gated Local-Context Attention** ensures precise audio-visual synchronization. It packs audio features with sufficient contextual information and injects them via masked attention to align video frames with corresponding audio segments, followed by adaptive gating to stabilize early training.
3. **Decoupled-Then-Joint Training** makes the efficient utilization of heterogeneous datasets possible. We first train specialized R2V and A2V models on separate sub-task datasets, then fuse them via weight interpolation, followed by joint fine-tuning to unify multimodal capabilities.

<div align="center">
  <img width="1080" alt="OmniShow Pipeline" src="assets/pipeline.png">
</div>


<br>

<details>
<summary>Learn more details</summary>

## 📊 HOIVG-Bench

To systematically evaluate HOIVG under diverse multimodal conditions, we construct **HOIVG-Bench**, a dedicated benchmark with 135 carefully curated samples and task-specific metrics. Each sample contains a detailed text caption, a human reference image, an object reference image, semantically aligned audio, and a coherent pose sequence.

<div align="center">
  <img width="1080" alt="HOIVG-Bench" src="assets/bench_example.png">
</div>


## 🎬 Demo

Across varied tasks, OmniShow exhibits high-fidelity reference preservation, natural motion dynamics, and precise audio-visual synchronization. Please visit the [OmniShow project page](https://correr-zhou.github.io/OmniShow/) for more immersive and diverse video demonstrations.

<div align="center">
  <img width="1080" alt="OmniShow Qualitative Results" src="assets/qual_results_more.png">
</div>


## 🏆 Benchmark Evaluation

OmniShow achieves overall state-of-the-art performance across various multimodal generation tasks, and it is the only model that supports the full RAP2V setting.

### Reference-to-Video Generation (R2V)

| Method | TA↑ | FaceSim↑ | NexusScore↑ | AES↑ | IQA↑ | VQ↑ | MQ↑ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| HunyuanCustom | 7.523 | 0.440 | 0.359 | 0.452 | 0.697 | 10.11 | 5.286 |
| HuMo-1.7B | 7.087 | 0.647 | 0.333 | 0.441 | 0.723 | 9.76 | 3.406 |
| HuMo-17B | 7.949 | 0.843 | 0.346 | 0.448 | 0.726 | 9.97 | 3.685 |
| VACE | <u>8.413</u> | 0.759 | <u>0.368</u> | 0.457 | 0.722 | 10.72 | 5.442 |
| Phantom-1.3B | 8.342 | 0.708 | 0.351 | <u>0.459</u> | 0.722 | 10.90 | <u>5.637</u> |
| Phantom-14B | **8.609** | **0.876** | 0.366 | 0.449 | **0.741** | <u>10.93</u> | 5.517 |
| OmniShow (Ours) | 7.746 | <u>0.874</u> | **0.389** | **0.468** | <u>0.740</u> | **11.12** | **5.885** |

### Reference+Audio-to-Video Generation (RA2V)

| Method | TA↑ | FaceSim↑ | NexusScore↑ | Sync-C↑ | Sync-D↓ | AES↑ | IQA↑ | VQ↑ | MQ↑ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| HunyuanCustom | 7.289 | 0.457 | <u>0.350</u> | 6.072 | 10.08 | <u>0.439</u> | 0.715 | 9.15 | 3.658 |
| HuMo-1.7B | 7.489 | 0.575 | 0.329 | 7.234 | 9.117 | 0.428 | 0.731 | 9.97 | 4.182 |
| HuMo-17B | **8.146** | <u>0.805</u> | 0.344 | <u>8.013</u> | <u>8.316</u> | 0.439 | <u>0.739</u> | <u>10.27</u> | <u>4.269</u> |
| OmniShow (Ours) | <u>8.093</u> | **0.810** | **0.369** | **8.612** | **7.608** | **0.465** | **0.742** | **10.86** | **5.554** |

### Reference+Pose-to-Video Generation (RP2V)

| Method | TA↑ | FaceSim↑ | NexusScore↑ | AKD↓ | PCK↑ | AES↑ | IQA↑ | VQ↑ | MQ↑ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| AnchorCrafter | 2.669 | 0.404 | 0.215 | 0.229 | 0.176 | **0.499** | 0.673 | 8.95 | 4.241 |
| VACE | **7.690** | **0.600** | <u>0.352</u> | <u>0.206</u> | <u>0.336</u> | <u>0.450</u> | <u>0.712</u> | <u>10.14</u> | **5.393** |
| OmniShow (Ours) | <u>6.526</u> | <u>0.474</u> | **0.418** | **0.174** | **0.460** | 0.447 | **0.722** | **10.28** | <u>4.937</u> |

</details>

## ✅ Todo List

- [x] Training Code (Wan-Based)
- [x] Inference Code (Wan-Based)
- [x] Data of HOIVG-Bench
- [x] Evaluation Code of HOIVG-Bench


## 🛠️ Environment Setup

We recommend using a clean Conda environment with Python 3.11:

```bash
git clone https://github.com/Correr-Zhou/OmniShow.git
cd OmniShow

conda create -n omnishow python=3.11 -y
conda activate omnishow

pip install -e .
pip install -r requirements.txt
```

If the default PyTorch installation does not match your CUDA version, reinstall PyTorch manually. For example, for CUDA 12.4:

```bash
pip install --index-url https://download.pytorch.org/whl/cu124 \
  torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0
```


## 📦 Data and Model Preparation

Download the required Wan backbones, tokenizer assets, Wav2Vec2 audio encoder, and the OmniShow example dataset:

```bash
bash download_weights.sh
bash download_data.sh
```


By default, the scripts organize files as:

```text
OmniShow/
├── models/
│   ├── Wan-AI/Wan2.1-I2V-14B-480P/
│   ├── Wan-AI/Wan2.1-I2V-14B-720P/
│   ├── Wan-AI/Wan2.1-T2V-1.3B/
│   └── facebook/wav2vec2-base-960h/
└── data/
    └── donghao-zhou/OmniShow_example_dataset/
```

The example dataset follows the metadata format below:

| Field | Description |
| :--- | :--- |
| `text_prompt` | Text description of the target video. |
| `ref_image_human` | Relative path to the human reference image. |
| `ref_image_object` | Relative path to the object reference image. |
| `audio` | Relative path to the audio file. |
| `audio_caption` | Textual description of the audio content. |
| `pose_video` | Relative path to the pose video. |
| `target_video` | Relative path to the training target video. Used for training metadata. |

This release focuses on reproducing our method on Wan-based models. Checkpoints are not included due to internal policy constraints.
The `target_video` files of the example dataset are generated by OmniShow and intended for checking that the code runs correctly.
For HOIVG-Bench, please download the benchmark from [HuggingFace](https://huggingface.co/datasets/donghao-zhou/HOIVG-Bench).


## ⚡ Quick Start

### Training

Run the default Wan-based OmniShow training script:

```bash
bash run_train/train_omnishow_wan.sh
```

The default script uses the example dataset and trains the `r2v` setting at `480p`. You can edit the following variables in `run_train/train_omnishow_wan.sh` to switch task, resolution, or data path:

```bash
GEN_TASK="r2v"      # r2v / a2v / ra2v / rp2v / rap2v
RESOLUTION="480p"  # 480p / 720p
DATA_FILE="data/donghao-zhou/OmniShow_example_dataset/meta_data_train.csv"
DATASET_BASE_PATH="data/donghao-zhou/OmniShow_example_dataset"
```

The training entry also supports direct command-line usage:

```bash
accelerate launch --config_file run_train/accelerate_config_14B_zero3.yaml \
  --num_processes 8 \
  run_train/train_omnishow_wan.py \
  --dataset_base_path data/donghao-zhou/OmniShow_example_dataset \
  --dataset_metadata_path data/donghao-zhou/OmniShow_example_dataset/meta_data_train.csv \
  --height 832 \
  --width 480 \
  --num_frames 49 \
  --gen_task r2v \
  --model_id_with_origin_paths "Wan-AI/Wan2.1-I2V-14B-480P:diffusion_pytorch_model*.safetensors,Wan-AI/Wan2.1-I2V-14B-480P:models_t5_umt5-xxl-enc-bf16.pth,Wan-AI/Wan2.1-I2V-14B-480P:Wan2.1_VAE.pth,Wan-AI/Wan2.1-I2V-14B-480P:models_clip_open-clip-xlm-roberta-large-vit-huge-14.pth" \
  --trainable_models "dit" \
  --learning_rate 1e-5 \
  --num_epochs 1000 \
  --save_steps 500 \
  --remove_prefix_in_ckpt "pipe.dit." \
  --output_path outputs/train_omnishow_wan_r2v_480p \
  --use_gradient_checkpointing_offload \
  --initialize_model_on_cpu
```

### Inference

Run the default Wan-based OmniShow inference script:

```bash
bash run_infer/infer_omnishow_wan.sh
```

The default script reads `meta_data_infer.csv` and saves generated videos to `outputs/`. To use a fine-tuned checkpoint, set `DIT_CHECKPOINT` in `run_infer/infer_omnishow_wan.sh`:

```bash
DIT_CHECKPOINT="path/to/your/checkpoint.safetensors"
```

The inference entry also supports direct command-line usage:

```bash
python run_infer/infer_omnishow_wan.py \
  --model_id Wan-AI/Wan2.1-I2V-14B-480P \
  --csv data/donghao-zhou/OmniShow_example_dataset/meta_data_infer.csv \
  --base_path data/donghao-zhou/OmniShow_example_dataset \
  --output_dir outputs/infer_omnishow_wan_r2v_480p \
  --gen_task r2v \
  --dit_checkpoint path/to/your/checkpoint.safetensors \
  --height 832 \
  --width 480 \
  --num_frames 49 \
  --num_inference_steps 50 \
  --cfg_scale 6 \
  --seed 42
```


## 🧭 Advanced Usage

OmniShow supports the following tasks:

| Task | Conditions | Typical inference CSV fields |
| :--- | :--- | :--- |
| `r2v` | text + reference images | `text_prompt`, `ref_image_human`, `ref_image_object` |
| `a2v` | text + first frame + audio | `text_prompt`, `input_image`, `audio` |
| `ra2v` | text + reference images + audio | `text_prompt`, `ref_image_human`, `ref_image_object`, `audio` |
| `rp2v` | text + reference images + pose | `text_prompt`, `ref_image_human`, `ref_image_object`, `pose_video` |
| `rap2v` | text + reference images + audio + pose | `text_prompt`, `ref_image_human`, `ref_image_object`, `audio`, `pose_video` |

Both training and inference scripts expose the same task switch:

```bash
GEN_TASK="r2v"  # r2v / a2v / ra2v / rp2v / rap2v
```

To switch resolution, you can also edit `RESOLUTION` in the corresponding script:

```bash
RESOLUTION="480p"  # 480p / 720p
```

The scripts automatically select the matching base model.

If you use a custom aspect ratio or resolution, also check the `HEIGHT` and `WIDTH` values in the script.

For training, the most commonly edited variables in `run_train/train_omnishow_wan.sh` are:

```bash
GEN_TASK="r2v"
RESOLUTION="480p"
DATA_FILE="path/to/your/meta_data_train.csv"
DATASET_BASE_PATH="path/to/your/dataset_root"
OUTPUT_DIR="outputs/train_omnishow_wan_${GEN_TASK}_${RESOLUTION}"
LAUNCH_NUM_PROCESSES=8
LEARNING_RATE="1e-5"
NUM_EPOCHS=1000
SAVE_STEPS=500
NUM_FRAMES=49
```

For inference, the most commonly edited variables in `run_infer/infer_omnishow_wan.sh` are:

```bash
GEN_TASK="r2v"
RESOLUTION="480p"
DATA_FILE="path/to/your/meta_data_infer.csv"
DATASET_BASE_PATH="path/to/your/dataset_root"
OUTPUT_DIR="outputs/infer_omnishow_wan_${GEN_TASK}_${RESOLUTION}"
DIT_CHECKPOINT="path/to/your/checkpoint.safetensors"
NUM_INFERENCE_STEPS=50
CFG_SCALE=6
SEED=42
```

If `DIT_CHECKPOINT` is left empty, inference uses the base Wan DiT weights. Set it when evaluating a fine-tuned checkpoint.


## 🧾 Preparing Your Own Dataset

To use your own data, follow the same CSV-driven format as the example dataset. All media paths in the CSV should be relative to `DATASET_BASE_PATH`.

A typical dataset can be organized as:

```text
your_dataset/
├── meta_data_train.csv
├── meta_data_infer.csv
├── ref_image_human/
├── ref_image_object/
├── input_image/
├── audio/
├── pose_video/
└── target_video/       # training only
```

Training metadata should include `target_video`, while inference metadata does not need it. For `a2v` training, the first frame is taken from `target_video`; for `a2v` inference, provide `input_image`.
The detailed requirements for CSV fields are as follows:

| Field | Required for | Description |
| :--- | :--- | :--- |
| `text_prompt` | all tasks | Text description of the target video. |
| `ref_image_human` | `r2v`, `ra2v`, `rp2v`, `rap2v` | Relative path to the human reference image. |
| `ref_image_object` | `r2v`, `ra2v`, `rp2v`, `rap2v` | Relative path to the object reference image. |
| `input_image` | `a2v` inference | Relative path to the first-frame image. |
| `audio` | `a2v`, `ra2v`, `rap2v` | Relative path to the audio file. |
| `audio_caption` | optional | Textual description of the audio content. |
| `pose_video` | `rp2v`, `rap2v` | Relative path to the pose video. |
| `target_video` | training only | Relative path to the target video used for supervision. Also provides the first frame for `a2v` training. |
| `output_name` | inference optional | Output filename stem for the generated video. |
| `negative_prompt` | inference optional | Per-sample negative prompt. If omitted, the default negative prompt is used. |
| `seed` | inference optional | Per-sample random seed. If omitted, the script-level seed is used. |

Example training row:

```csv
text_prompt,ref_image_human,ref_image_object,audio,audio_caption,pose_video,target_video
"A person presents a object to the camera.",ref_image_human/0001.png,ref_image_object/0001.png,audio/0001.wav,"Object introduction speech.",pose_video/0001.mp4,target_video/0001.mp4
```

Example inference row:

```csv
text_prompt,ref_image_human,ref_image_object,audio,audio_caption,pose_video,output_name
"A person presents a object to the camera.",ref_image_human/0001.png,ref_image_object/0001.png,audio/0001.wav,"Object introduction speech.",pose_video/0001.mp4,sample_0001
```


## 🗂️ File Structure

The released code is organized around the OmniShow training and inference workflow:

```text
OmniShow/
├── assets/                         # Figures used in this README.
├── diffsynth/                       # Core framework and OmniShow implementation.
│   ├── configs/
│   ├── core/
│   ├── diffusion/
│   ├── models/
│   ├── modules/
│   ├── pipelines/
│   ├── utils/
│   ├── __init__.py
│   └── version.py
├── run_train/                      # Training entrypoint, launcher script, and Accelerate config.
│   ├── accelerate_config_14B_zero3.yaml
│   ├── train_omnishow_wan.py
│   └── train_omnishow_wan.sh
├── run_infer/                      # Inference entrypoint and example launcher script.
│   ├── infer_omnishow_wan.py
│   └── infer_omnishow_wan.sh
├── evaluation/                     # HOIVG-Bench evaluation pipeline and vendored metric adapters.
├── download_weights.sh             # Downloads Wan, tokenizer, and audio encoder weights.
├── download_data.sh                # Downloads the OmniShow example dataset.
├── requirements.txt                # Python dependencies used by the release.
└── README.md                       # Project overview and usage instructions.
```


## 📊 Evaluation

The `evaluation/` folder provides the HOIVG-Bench evaluation pipeline. It runs the selected metric families with separate evaluator environments and merges the results into a unified `final_report.csv`. For environment setup, checkpoint preparation, input format, and usage commands, please see the [evaluation README](evaluation/README.md).


## ⚖️ Ethics

OmniShow is released for research purposes. The code and data are intended to support responsible study of video generation. Please follow the following guidelines:

- Do not use the model for identity misuse, impersonation, harassment, deception, or other harmful content generation.
- Respect the licenses and usage restrictions of the underlying Wan models, Wav2Vec2, datasets, and any input media.
- When using personal images, voices, or videos, obtain proper consent and follow applicable laws and platform policies.
- Generated content should be clearly disclosed when used in public-facing scenarios.


## 🤝 Acknowledgements

This codebase was built upon [DiffSynth-Studio](https://github.com/modelscope/diffsynth-studio). We sincerely thank the contributors of this project for their excellent code.



## 🔗 Citation

If you find OmniShow useful or inspiring, please consider giving us a ⭐ on GitHub. Your support helps more people discover the project!

If OmniShow is helpful for your research or projects, please consider citing our work:

```bibtex
@article{zhou2026omnishow,
  title={OmniShow: Unifying Multimodal Conditions for Human-Object Interaction Video Generation},
  author={Zhou, Donghao and Liu, Guisheng and Yang, Hao and Li, Jiatong and Lin, Jingyu and Huang, Xiaohu and Liu, Yichen and Gao, Xin and Chen, Cunjian and Wen, Shilei and Fu, Chi-Wing and Heng, Pheng-Ann},
  journal={arXiv preprint arXiv:2604.11804},
  year={2026}
}
```

## 📬 Contact

For questions about OmniShow, please contact Donghao Zhou at [dhzhou@link.cuhk.edu.hk](mailto:dhzhou@link.cuhk.edu.hk).
