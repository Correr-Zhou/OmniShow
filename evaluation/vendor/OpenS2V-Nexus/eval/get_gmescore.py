import os
import json
import numpy as np
from PIL import Image
import argparse
from utils.gme.gme_model import GmeQwen2VL
from tqdm import tqdm
import torch
import decord

os.environ["TOKENIZERS_PARALLELISM"] = "false"
# os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True" # Already set in runner


def sample_video_frames(video_path, num_frames=16):
    vr = decord.VideoReader(video_path)
    total_frames = len(vr)

    if num_frames is None:
        frame_indices = np.arange(total_frames)
    else:
        frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    frames = []
    for idx in frame_indices:
        frame = vr[int(idx)].asnumpy()
        pil_image = Image.fromarray(frame)
        frames.append(pil_image)

    return frames


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_video_folder",
        type=str,
        default="demo_result/model_name_input_video",
    )
    parser.add_argument(
        "--input_json_file",
        type=str,
        default="demo_result/input_json/Open-Domain_Eval.json",
    )
    parser.add_argument(
        "--output_json_folder",
        type=str,
        default="demo_result/model_name_output_json",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default="Alibaba-NLP/gme-Qwen2-VL-7B-Instruct",
    )
    parser.add_argument("--num_frames", type=int, default=32)
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size for inference to avoid OOM")
    return parser.parse_args()


import torch

def main():
    args = parse_args()
    device = "cuda"

    input_video_folder = args.input_video_folder
    input_json_file = args.input_json_file
    output_json_folder = args.output_json_folder
    model_path = args.model_path
    num_frames = args.num_frames
    batch_size = args.batch_size

    output_json_file = os.path.join(output_json_folder, "gmescore.json")
    os.makedirs(output_json_folder, exist_ok=True)
    if os.path.exists(output_json_file):
        print("continue")
        return

    with open(input_json_file, "r") as f:
        prompts = json.load(f)
    
    # Try to use flash_attention_2 if available for better memory efficiency
    # If it fails (e.g. ABI issues), fallback to sdpa
    attn_implementation = "sdpa"
    try:
        # Simple check if flash_attn is importable
        import flash_attn
        attn_implementation = "flash_attention_2"
        print("[GmeScore] Flash Attention 2 is available. Using it for memory efficiency.")
    except ImportError:
        print("[GmeScore] Flash Attention 2 not found. Falling back to SDPA.")
    except Exception as e:
        print(f"[GmeScore] Warning checking Flash Attention: {e}. Falling back to SDPA.")

    try:
        gme = GmeQwen2VL(model_path, attn_model=attn_implementation, device=device)
    except Exception as e:
        print(f"[GmeScore] Failed to init with {attn_implementation}: {e}. Retrying with sdpa...")
        gme = GmeQwen2VL(model_path, attn_model="sdpa", device=device)

    video_files = [f for f in os.listdir(input_video_folder) if f.endswith(".mp4")]

    results_dict = {}
    for video_filename in tqdm(video_files, desc="Processing videos"):
        video_name = os.path.splitext(video_filename)[0]

        if video_name in prompts.keys():
            text_prompt = prompts[video_name].get("prompt", "")
        else:
            print(f"No prompt found for video: {video_name}. Skipping.")
            continue

        video_path = os.path.join(input_video_folder, video_filename)
        frames = sample_video_frames(video_path, num_frames=num_frames)
        
        # Clear cache before processing new video
        torch.cuda.empty_cache()

        e_query = gme.get_text_embeddings(
            texts=[text_prompt] * len(frames),
            instruction="Find an image that matches the given text.",
            batch_size=batch_size,
        )
        e_corpus = gme.get_image_embeddings(
            images=frames, is_query=False, show_progress_bar=False,
            batch_size=batch_size,
        )
        gme_scores = (e_query * e_corpus).sum(-1)
        gme_score = gme_scores.mean().detach().item()

        results_dict[video_name] = {"gme_score": gme_score}
        
        # Clean up tensors to free graph
        del e_query
        del e_corpus
        del gme_scores
        del frames
        
        # Aggressive cleanup
        torch.cuda.empty_cache()

    with open(output_json_file, "w") as results_file:
        json.dump(results_dict, results_file, indent=4)

    print(f"All results have been saved to {output_json_file}")


if __name__ == "__main__":
    main()
