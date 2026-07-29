<div align=center>
<img src="https://github.com/PKU-YuanGroup/OpenS2V-Nexus/blob/main/__assets__/OpenS2V-Nexus_logo.png?raw=true" width="300px">
</div>
<h2 align="center"> <a href="https://arxiv.org/abs/2505.20292">OpenS2V-Nexus: A Detailed Benchmark and Million-Scale Dataset for Subject-to-Video Generation</a></h2>

<h5 align="center"> If you like our project, please give us a star ⭐ on GitHub for the latest update.  </h2>


<h5 align="center">

[![hf_space](https://img.shields.io/badge/🤗-Leaderboard-blue.svg)](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval)
[![hf_paper](https://img.shields.io/badge/🤗-Paper%20In%20HF-red.svg)](https://huggingface.co/papers/2505.20292)
[![arXiv](https://img.shields.io/badge/Arxiv-2505.20292-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2505.20292) 
[![Home Page](https://img.shields.io/badge/Project-<Website>-blue.svg)](https://pku-yuangroup.github.io/OpenS2V-Nexus) 
[![Dataset](https://img.shields.io/badge/Dataset-OpenS2V_5M-green)](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M)
[![Dataset](https://img.shields.io/badge/Benchmark-OpenS2V_Eval-green)](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval)
[![Dataset Download](https://img.shields.io/badge/Result-Sampled_Videos-red)](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results)
[![License](https://img.shields.io/badge/License-Apache%202.0-yellow)](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/blob/main/LICENSE) 
[![github](https://img.shields.io/github/stars/PKU-YuanGroup/OpenS2V-Nexus.svg?style=social)](https://github.com/PKU-YuanGroup/OpenS2V-Nexus)



</h5>

<div align="center">
This repository is the official implementation of <strong>OpenS2V-Nexus</strong>, consisting of (i) <strong>OpenS2V‑Eval</strong>, a fine‑grained benchmark, and (ii) <strong>OpenS2V‑5M</strong>, a million‑scale dataset. Our goal is to establish the infrastructure for Subject-to-Video generation, thereby empowering the community.
</div>


<br>

<details open><summary>💡 We also have other video generation projects that may interest you ✨. </summary><p>
<!--  may -->

> [**Open-Sora Plan: Open-Source Large Video Generation Model**](https://arxiv.org/abs/2412.00131) <br>
> Bin Lin, Yunyang Ge and Xinhua Cheng etc. <br>
[![github](https://img.shields.io/badge/-Github-black?logo=github)](https://github.com/PKU-YuanGroup/Open-Sora-Plan)  [![github](https://img.shields.io/github/stars/PKU-YuanGroup/Open-Sora-Plan.svg?style=social)](https://github.com/PKU-YuanGroup/Open-Sora-Plan) [![arXiv](https://img.shields.io/badge/Arxiv-2412.00131-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2412.00131) <br>
>
> [**ConsisID: Identity-Preserving Text-to-Video Generation by Frequency Decomposition**](https://arxiv.org/abs/2411.17440) <br>
> Shenghai Yuan, Jinfa Huang and Xianyi He etc. <br>
> [![github](https://img.shields.io/badge/-Github-black?logo=github)](https://github.com/PKU-YuanGroup/ConsisID/)  [![github](https://img.shields.io/github/stars/PKU-YuanGroup/ConsisID.svg?style=social)](https://github.com/PKU-YuanGroup/ConsisID/) [![arXiv](https://img.shields.io/badge/Arxiv-2411.17440-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2411.17440) <br>
>
> [**MagicTime: Time-lapse Video Generation Models as Metamorphic Simulators**](https://arxiv.org/abs/2404.05014) <br>
> Shenghai Yuan, Jinfa Huang and Yujun Shi etc. <br>
> [![github](https://img.shields.io/badge/-Github-black?logo=github)](https://github.com/PKU-YuanGroup/MagicTime)  [![github](https://img.shields.io/github/stars/PKU-YuanGroup/MagicTime.svg?style=social)](https://github.com/PKU-YuanGroup/MagicTime) [![arXiv](https://img.shields.io/badge/Arxiv-2404.05014-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2404.05014) <br>
>
> [**ChronoMagic-Bench: A Benchmark for Metamorphic Evaluation of Text-to-Time-lapse Video Generation**](https://arxiv.org/abs/2406.18522) <br>
> Shenghai Yuan, Jinfa Huang and Yongqi Xu etc. <br>
> [![github](https://img.shields.io/badge/-Github-black?logo=github)](https://github.com/PKU-YuanGroup/ChronoMagic-Bench/)  [![github](https://img.shields.io/github/stars/PKU-YuanGroup/ChronoMagic-Bench.svg?style=social)](https://github.com/PKU-YuanGroup/ChronoMagic-Bench/) [![arXiv](https://img.shields.io/badge/Arxiv-2406.18522-b31b1b.svg?logo=arXiv)](https://arxiv.org/abs/2406.18522) <br>
> </p></details>


## 📣 News

* ⏳⏳⏳ Evaluating more models and updating the [![hf_space](https://img.shields.io/badge/🤗-Leaderboard-blue.svg)](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval). PRs are welcome!
* `[2026.01.08]`  🏃‍♂️ We add the evaluation results for [VINO](https://sotamak1r.github.io/VINO-web); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) for details.
* `[2026.01.07]`  🔥 We release the **high-quality subset**. It’s not just 0.3M samples — we applied filtering across the entire **5M data**. You can click [here](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/blob/main/data_process/README.md#step-7---fetch-high-quality-subset) for more details, and click [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M/tree/main/Jsons/mask_and_bbox_High-Quality) to download.
* `[2026.01.06]`  🚀 We will release the **high-quality subset** very soon! Stay tuned!
* `[2025.12.05]`  🏃‍♂️ We add the evaluation results for [Saber](https://franciszzj.github.io/Saber); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) for details.
* `[2025.11.04]`  🚀 Great work on [BindWeave](https://github.com/bytedance/BindWeave)! The team has open-sourced the entire codebase, including the pipeline for **training with OpenS2V-5M** and **evaluation on OpenS2V-Eval**. You can refer to this repository as a practical example of how to use OpenS2V-Nexus.
* `[2025.10.21]`  🏃‍♂️ We add the evaluation results for [Stand-In](https://github.com/WeChatCV/Stand-In) and [BindWeave](https://lzy-dot.github.io/BindWeave); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) and [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results) for details.
* `[2025.09.19]` ✨ Our paper is accepted by **NeurIPS 2025 D&B**!
* `[2025.08.30]`  🚀 Thanks for the excellent work [DanceGRPO](https://github.com/XueZeyue/DanceGRPO) on transferring [ConsisID data](https://github.com/PKU-YuanGroup/ConsisID) for I2V RL training, please refer to [here](https://github.com/XueZeyue/DanceGRPO?tab=readme-ov-file#training) for more details. Similarly, you can also try using OpenS2V-5M for RL training.
* `[2025.08.05]`  🔥 We provide a [dev version](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Hard-Case_Dev_Eval) that increases the max number of subject images in OpenS2V-Eval to 5, and have uploaded [results](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Hard-Case_Dev_Eval/Results_dev) for Vidu-Q1, Vidu-2.0, and Kling1.6. Also, [OpenS2V-Eval-Leaderboard v1.1](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval/tree/main/file_v1.1) is out, which introduces Motion Smoothness score for improved motion quality measurement.
* `[2025.07.01]`  🎉 Thanks to our amazing community — the [OpenS2V-5M](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M) dataset has reached ~40,000 downloads on Hugging Face in just one month! 
* `[2025.06.21]`  🏃‍♂️ We add the evaluation results for [MAGREF-480P](https://github.com/MAGREF-Video/MAGREF); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) and [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results) for details.
* `[2025.06.19]`  🔥 The preprocessed *Cross-Frame Pairs* is now available on [Hugging Face](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M/tree/main/Jsons/cross_video_pairs), eliminating the need for online processing with this [code](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/blob/main/data_process/step6-2_get_cross-frame.py) during training. We also provide a demo dataloader [here](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/blob/main/data_process/demo_dataloader.py) demonstrating how to use OpenS2V-5M during the training phase.
* `[2025.05.31]`  🏃‍♂️ We add the evaluation results for [Concat-ID-Wan-AdaLN](https://github.com/ML-GSAI/Concat-ID); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) and [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results) for details.
* `[2025.05.28]`  🏃‍♂️ We add the evaluation results for [Phantom-14B](https://github.com/Phantom-video/Phantom); click [here](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) and [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results) for details.
* `[2025.05.27]`  🔥 Our **arXiv** paper on OpenS2V-Nexus is now available; click [here](https://arxiv.org/abs/2505.20292) for details.
* `[2025.05.26]`  🔥 **All codes & datasets** are out! We also release the **testing prompts**, **reference images** and **videos generated by different models** in *OpenS2V-Eval*, and you can click [here](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results) to see more details.


## 💡 Community Works
If your research or project builds upon [**OpenS2V-5M**](https://github.com/PKU-YuanGroup/OpenS2V-Nexus) or [**OpenS2V-Eval**](https://github.com/PKU-YuanGroup/OpenS2V-Nexus), and you would like more people to see it, please inform us.

- [VINO](https://sotamak1r.github.io/VINO-web), a unified framework for image and video generation and editing. It uses a shared diffusion backbone and interleaved conditioning to enable multi-reference grounding, instruction following, and consistent identity preservation across modalities within a single model.
- [Saber](https://franciszzj.github.io/Saber), a zero-shot reference-to-video framework that generates identity-consistent videos from text and reference images without explicit R2V training data, using masked video frames as self-supervision and attention-guided learning to support flexible multi-subject customization.
- [ID-Composer](https://arxiv.org/abs/2511.00511), a reinforcement learning-based multi-subject video generation framework that synthesizes high-quality, identity-consistent videos from text prompts and reference images through hierarchical identity-preserving attention and vision-language model semantic guidance.
- [BindWeave](https://lzy-dot.github.io/BindWeave), a unified framework that uses multimodal large language model reasoning to disentangle complex prompt semantics and generate high-fidelity, subject-consistent videos across diverse single- and multi-subject scenarios.
- [Humo](https://phantom-video.github.io/HuMo), a unified, human-centric video generation framework designed to produce high-quality, fine-grained, and controllable human videos from multimodal inputs—including text, images, and audio. It supports strong text prompt following, consistent subject preservation, synchronized audio-driven motion.
- [Stand-In](https://www.stand-in.tech/), a lightweight, plug-and-play framework for identity-preserving video generation.  By training only 1% additional parameters compared to the base video generation model, they achieve state-of-the-art results in both Face Similarity and Naturalness, outperforming various full-parameter training methods.
- [MagRef](https://magref-video.github.io), a unified video generation framework that uses masked guidance to achieve high-quality, multi-subject consistent video synthesis from multiple reference images and text prompts.


## ✨ Highlights

1. **New S2V Benchmark.** 
   - We introduce *OpenS2V-Eval* for comprehensive evaluation of S2V models and propose three new automatic metrics aligned with human perception.
2. **New Insights for S2V Model Selection.**
   - Our evaluations using *OpenS2V-Eval* provide crucial insights into the strengths and weaknesses of various subject-to-video generation models.
3. **Million-Scale S2V Dataset.** 
   - We create *OpenS2V-5M*, a dataset with 5.1M high-quality regular data and 0.35M Nexus Data, the latter is expected to address the three core challenges of subject-to-video.

#### Resources
* [OpenS2V-Eval](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval): including 180 *open-domain* subject-text pairs, of which 80 are real and 100 are synthetic samples.
* [OpenS2V-5M](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M): including **5M** *open-domain* subject-text-video triples, which not only include Regular Data but also incorporate Nexus Data constructed using GPT-Image-1 and cross-video associations.
* [ConsisID-Bench](https://huggingface.co/datasets/BestWishYsh/ConsisID-preview-Data/tree/main/eval): including 150 *human-domain* subject images and 90 text prompts, respectively.
* [ConsisID-Preview-Data](https://huggingface.co/datasets/BestWishYsh/ConsisID-preview-Data): including **32K** *human-domain* high-quality subject-text-video triples.

## 😍 In-house Model Gallery 
This model (Ours‡) was trained on a subset of OpenS2V-5M, using about 0.3M high-quality data.
<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/bd56d23c-084b-433c-a12d-49b36b2bb7d8" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/cca7680e-606d-4d9b-b7d2-b2c1db7810d4" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/a028468a-0152-4c0c-bdb8-bc5095fc2d60" controls style="width:100%"></video></td> 
  </tr>
  <tr>
  	<td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/653d7d60-44ac-424c-bd19-3c1f3328648c" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/5910f003-05ba-4731-8f34-b7c7a1461eb0" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/95cab48d-746c-41cc-8f60-abe1191abe22" controls style="width:100%"></video></td>
    </video></td>
  </tr>
  <tr>
  	<td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/83d7bc62-edd0-4bb9-a771-56addad26311" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/c7f86ea2-0308-49e9-a4b9-f59b56aac01b" controls style="width:100%">
  	<td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/45eab9a3-6344-4acc-a9ff-1f8bcbb69eb8" controls style="width:100%"></video></td>
  </tr>
</table>

## ⚙️ Requirements and Installation

We recommend the requirements as follows.

### Base Environment

```bash
# 0. Clone the repo
git clone --depth=1 https://github.com/PKU-YuanGroup/OpenS2V-Nexus.git
cd OpenS2V-Nexus

# 1. Create conda environment
conda create -n opens2v python=3.12.0
conda activate opens2v

# 3. Install PyTorch and other dependencies
# CUDA 11.8
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu118
pip install flashinfer-python==0.2.2.post1 -i https://flashinfer.ai/whl/cu118/torch2.6
# CUDA 12.4
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124
pip install flashinfer-python==0.2.2.post1 -i https://flashinfer.ai/whl/cu124/torch2.6

# 4. Install main dependencies
pip install -r requirements.txt
pip install flash-attn --no-build-isolation
```

### Base Checkpoints

```bash
cd OpenS2V-Nexus

huggingface-cli download --repo-type model \
BestWishYsh/OpenS2V-Weight \
--local-dir ckpts
```

Once ready, the weights will be organized in this format:

```bash
📦 OpenS2V-Nexus/
├── 📂 LaMa
├── 📂 face_extractor
├── 📄 aesthetic-model.pth
├── 📄 glint360k_curricular_face_r101_backbone.bin
├── 📄 groundingdino_swint_ogc.pth
├── 📄 sam2.1_hiera_large.pt
├── 📄 yolo_world_v2_l_image_prompt_adapter-719a7afb.pth
```

## 🗝️ Benchmark

### OpenS2V-Eval Results

<p align="center">
  <img src="https://github.com/user-attachments/assets/2ea5a89f-85f3-4060-98fb-22bdad50c374"/>
</p>

We visualize the evaluation results of various Subject-to-Video generation models across *Open-Domain*, *Human-Domain* and *Single-Object*.

### Get Videos Generated by Different S2V models

[![Dataset Download](https://img.shields.io/badge/Result-Sampled_Videos-red)](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results)

To facilitate future research and to ensure full transparency, we release all the videos we sampled and used for *OpenS2V-Eval* evaluation. You can download them on [Hugging Face](https://huggingface.co/datasets/BestWishYsh/OpenS2V-Eval/tree/main/Results). We also provide detailed explanations of the sampled videos and detailed setting for the models under evaluation [here](https://arxiv.org/abs/2505.20292).

### Leaderboard

See numeric values at our [Leaderboard](https://huggingface.co/spaces/BestWishYsh/OpenS2V-Eval) :1st_place_medal::2nd_place_medal::3rd_place_medal:

or you can run it locally:

```bash
cd leaderboard
python app.py
```
### Evaluate Your Own Models

Please refer to [this guide](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/tree/main/eval) for how to evaluate customized models.

## 🤗 Dataset

### Subject-Text-Video Triples in OpenS2V-5M

<table style="width:100%; border-collapse: collapse; margin: 20px 0;">
  <tr>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/399b2e42-dd9a-4f3b-aaf7-af309e6628e9" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/be6ec4ac-7016-4ed7-99fe-48f5f909036b" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/bf2a95b2-bbfb-4b65-a6f2-fc2f17449d36" controls style="width:100%"></video></td>
  </tr>
  <tr>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/5ee0e4c8-45f4-4c74-a705-1a41ee33a89f" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/7d04ce33-084f-4351-b253-c99909dd2a63" controls style="width:100%"></video></td>
    <td style="padding: 10px;"><video src="https://github.com/user-attachments/assets/4ed90def-0d9e-4ba5-aec3-a0deac77f0bd" controls style="width:100%"></video></td>
  </tr>
</table>

### Get the Data

We release the subset of the *OpenS2V-5M*. The dataset is available at [HuggingFace](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M), or you can download it with the following command. Some samples can be found on our [Project Page](https://pku-yuangroup.github.io/OpenS2V-Nexus/).

```bash
huggingface-cli download --repo-type dataset \
BestWishYsh/OpenS2V-5M \
--local-dir BestWishYsh/OpenS2V-5M
```

### Usage of OpenS2V-5M

Please refer to [this guide](https://huggingface.co/datasets/BestWishYsh/OpenS2V-5M#%F0%9F%93%A3-usage) for how to use OpenS2V-5M dataset.

### Process Your Own Videos

Please refer to [this guide](https://github.com/PKU-YuanGroup/OpenS2V-Nexus/tree/main/data_process) for how to process customized videos.

## 👍 Acknowledgement

* This project wouldn't be possible without the following open-sourced repositories: [Open-Sora Plan](https://github.com/PKU-YuanGroup/Open-Sora-Plan), [Video-Dataset-Scripts](https://github.com/huggingface/video-dataset-scripts/tree/main), [YOLO-World](https://github.com/AILab-CVC/YOLO-World), [Grounded-SAM-2](https://github.com/IDEA-Research/Grounded-SAM-2), [improved-aesthetic-predictor](https://github.com/christophschuhmann/improved-aesthetic-predictor), [Qwen2.5-VL](https://github.com/QwenLM/Qwen2.5-VL), [vllm](https://github.com/vllm-project/vllm), [VBench](https://github.com/Vchitect/VBench), [ChronoMagic-Bench](https://github.com/PKU-YuanGroup/ChronoMagic-Bench), [Phantom](https://github.com/Phantom-video/Phantom), [VACE](https://github.com/ali-vilab/VACE), [SkyReels-A2](https://github.com/SkyworkAI/SkyReels-A2), [HunyuanCustom](https://github.com/Tencent-Hunyuan/HunyuanCustom), [ConsisID](https://github.com/PKU-YuanGroup/ConsisID), [Concat-ID](https://github.com/ML-GSAI/Concat-ID), [Fantasy-ID](https://github.com/Fantasy-AMAP/fantasy-id), [EchoVideo](https://github.com/bytedance/EchoVideo).

## 🔒 License

* The majority of this project is released under the Apache 2.0 license as found in the [LICENSE](https://github.com/PKU-YuanGroup/ConsisID/blob/main/LICENSE) file.
* The service is a research preview. Please contact us if you find any potential violations. (shyuan-cs@hotmail.com)

## ✏️ Citation

If you find our paper and code useful in your research, please consider giving a star :star: and citation :pencil:.

```BibTeX
@article{yuan2025opens2v,
  title={OpenS2V-Nexus: A Detailed Benchmark and Million-Scale Dataset for Subject-to-Video Generation},
  author={Yuan, Shenghai and He, Xianyi and Deng, Yufan and Ye, Yang and Huang, Jinfa and Lin, Bin and Luo, Jiebo and Yuan, Li},
  journal={arXiv preprint arXiv:2505.20292},
  year={2025}
}
```

## 🤝 Contributors

<a href="https://github.com/PKU-YuanGroup/OpenS2V-Nexus/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=PKU-YuanGroup/OpenS2V-Nexus&anon=true" />

</a>
