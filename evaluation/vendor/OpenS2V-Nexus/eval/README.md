# <u>Evaluation Pipeline</u> by *OpenS2V-Eval-v1.1*
This repo describes how to evaluate customized model like [OpenS2V-Eval](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval) in the [OpenS2V-Nexus](https://arxiv.org) paper.

The **v1.1** version adds motion smoothness on top of **v1.0** to provide a more accurate measurement of motion quality.

## 🎉 Overview

<div align=center>
<img src="https://github.com/user-attachments/assets/40470244-4712-42ee-917d-9dfdd7dcaecb">
</div>

## ⚙️ Requirements and Installation

We recommend the requirements as follows. You should first follow the [instructions](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/?tab=readme-ov-file#%EF%B8%8F-requirements-and-installation) to install the *Base Environment* and obtain the *Base Checkpoints*.

### Prepare Input Sample

The input sample is available at [HuggingFace](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval) and can be used to generate videos with your own models.

```bash
cd OpenS2V-Nexus

huggingface-cli download --repo-type dataset \
BestWishYsh/OpenS2V-Eval \
--local-dir OpenS2V-Eval
```

Once ready, the test data will be organized in this format:

```bash
📦 OpenS2V-Eval/
├── 📂 Images/
├── 📂 Results/
├── 📄 Human-Domain_Eval.json
├── 📄 Open-Domain_Eval.json
├── 📄 Single-Domain_Eval.json
```

### Prepare Videos for Evaluation

Generate videos in the evaluation folder (structure shown below), naming them based on their sample IDs. Example inputs are provided in the `demo_result/model_name_input_video` folder.

```bash
# For Open-Domain Evaluation
📦 Generated_Videos/
├── 📄 singleobj_1.mp4
├── 📄 singleobj_2.mp4
├── 📄 ...
├── 📄 multiobject_30.mp4

# For Human-Domain Evaluation
📦 Generated_Videos/
├── 📄 singlehuman_1.mp4
├── 📄 singlehuman_2.mp4
├── 📄 ...
├── 📄 singleface_30.mp4

# For Sinlge-Domain Evaluation
📦 Generated_Videos/
├── 📄 singlehuman_1.mp4
├── 📄 singlehuman_2.mp4
├── 📄 ...
├── 📄 singleobj_30.mp4
```

The filenames of all videos to be evaluated should be *videoid.mp4*. For example, if the *videoid* is *multiobject_30*, the video filename should be *multiobject_30.mp4*. If this naming convention is not followed, the videos cannot be evaluated.

### Prepare Environment for YOLOWorld

```bash
# 0. Create conda environment
conda create -n opens2v_yoloworld python=3.10
conda activate opens2v_yoloworld

# 1. Install PyTorch and other dependencies
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121 # or cu118
#ensure your cuda version is 11.8 or 12.1, and ensure the gcc in a high version (we use 11.2)
pip install flash-attn --no-build-isolation

# 2. Install main dependencies
cd OpenS2V-Nexus/eval/utils/yoloworld
pip install mmcv==2.2.0 -f https://download.openmmlab.com/mmcv/dist/cu121/torch2.4/index.html --no-cache-dir # or cu118
pip install -r requirements.txt
pip install -e .
```

❗There will be an error about the mmcv version exceeds 2.1.0, users should directly change the `mmcv_maximum_version` to `2.3.0` in `Your_PATH_to_Anaconda/env/opens2v_yoloworld/lib/python3.10/site-packages/mmdet/__init__.py` and `Your_PATH_to_Anaconda/env/opens2v_yoloworld/lib/python3.10/site-packages/mmyolo/__init__.py`

### Prepare Environment for Q-Align
```bash
# 0. Create conda environment
conda create -n opens2v_qalign python=3.10
conda activate opens2v_qalign

# 1. Install PyTorch and other dependencies
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cu121 # or cu118
#ensure your cuda version is 11.8 or 12.1, and ensure the gcc in a high version (we use 11.2)
pip install flash-attn --no-build-isolation

# 2. Install main dependencies
cd OpenS2V-Nexus/eval/utils/Q-Align
pip install -e .
```

## 🗝️ Usage

 *<u>For all steps, we provide both input and output examples in the `demo_result` folder.</u>*

### Get Scores step by step

```bash
# 0. Use Base Environment
conda activate opens2v
# Get AestheticScore
python get_aesscore.py
# Get Motion Amplitude
python get_motion_amplitude.py

# Get FaceSim-Cur
python get_facesim.py
# Get GmeScore
python get_gmescore.py
# Get NaturalScore
python get_naturalscore.py

# 1. Use YOLOWorld Environment
conda activate opens2v_yoloworld
# Get NexusScore
python get_nexusscore.py

# 2. Use QAlign Environment
conda activate opens2v_qalign
# Get Motion Smoothness
python get_motion_smoothness.py
```

### Merge File and Submission

```bash
python merge_result.py
```

After completing the above steps, you will obtain [model_name_eval-type.json](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/tree/main/eval/demo_result/model_name_Open-Domain.json), and then you can submit it to the [LeaderBoard](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval).

## 🔒 Limitation

- Although NexusScore and NaturalScore are introduced to evaluate subject consistency and naturalness, these metrics show only approximately 75\% correlation with human preferences. Future work aims to better align automated metrics with human judgments.
