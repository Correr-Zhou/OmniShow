import os
import cv2
import json
import base64
import argparse
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from tenacity import retry, wait_exponential, stop_after_attempt


prompt = """
Your task is to determine how realistic the given video clip appears, based on 16 extracted frames. Consider the following aspects in your evaluation:

- **Common sense consistency**: Are the objects, people, and interactions logically coherent in the context of the video?
- **Physical plausibility**: Do lighting, shadows, motion, and reflections obey the laws of physics? Are the objects in motion consistent with real-world physics?
- **Naturalness**: Does the visual quality (textures, details, proportions, etc.) resemble what we would expect in real life? Is there any unnatural visual distortion?
- **AI generation artifacts**: Are there signs of unnatural blurring, morphing, glitches, distortions, or inconsistencies across frames? 

**If the video contains humans**, pay special attention to:
- Are the facial features realistic and anatomically correct (e.g., eyes, mouth, and nose proportions)?
- Do the body parts appear proportionate and natural in motion (e.g., arm and leg movements, hand gestures)?

If **no humans** are present in the video, you can focus on evaluating the realism of other visual aspects like object consistency, motion fluidity, and environmental plausibility without needing to specifically assess human-related elements.

Output a score from 1 to 5 based on the criteria below, followed by an explanation of the reasoning behind your score:

- **1 — Definitely AI-Generated**: Clear and frequent artifacts (e.g., blurry faces or objects, unnatural movements, inconsistent lighting), distorted shapes, implausible physics (e.g., impossible movements, lighting issues), and severe inconsistencies. Violates common sense or real-world logic. Faces and bodies may be unrealistic or distorted if humans are present.
- **2 — Likely AI-Generated**: Noticeable AI generation cues such as inconsistent anatomy, fluctuating object textures, or mild physical implausibility (e.g., unnatural hand positions or eye movements). Faces and bodies may appear unnatural or inconsistent if humans are present. Still clearly synthetic upon inspection.
- **3 — Uncertain / Borderline**: Mixed indicators — the video may appear mostly natural but contains subtle flaws or small anomalies that raise suspicion. Faces and bodies might show mild inconsistencies (e.g., slight distortion in facial features or body parts) if humans are present. Hard to determine definitively.
- **4 — Likely Real**: Mostly natural and physically plausible, with only minor and rare irregularities that might be explainable (e.g., slight compression, mild lighting inconsistencies). Faces and body parts are mostly natural, with only minor imperfections, if humans are present.
- **5 — Definitely Real**: Fully consistent with real-world physics, common sense, and appearance. No visible artifacts or signs of AI generation. Faces and body parts appear fully realistic, without any visible distortions or unnatural movements, if humans are present.

Please only return the score (1-5), no additional explanation.
"""


def image_to_base64(image):
    _, buffer = cv2.imencode(".jpg", image)
    return base64.b64encode(buffer).decode("utf-8")


def resize_long_side(image, target_long=512):
    h, w = image.shape[:2]
    if h >= w:
        new_h = target_long
        new_w = int(w * target_long / h)
    else:
        new_w = target_long
        new_h = int(h * target_long / w)
    return cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)


def extract_frames(video_path, num_frames=16):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(total_frames // num_frames, 1)
    frames = []

    for i in range(num_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i * frame_interval)
        ret, frame = cap.read()
        if ret:
            resized = resize_long_side(frame, 512)
            frames.append(resized)

    cap.release()
    return frames


@retry(wait=wait_exponential(min=2, max=10), stop=stop_after_attempt(5))
def call_gpt(
    image_frames_base64,
    video_name_prefix,
    model_name="gpt-4o-2024-11-20",
    api_key=None,
    base_url=None,
):
    client = OpenAI(api_key=api_key, base_url=base_url)
    content_list = []
    for frame in image_frames_base64:
        content_list.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{frame}"},
            }
        )
    content_list.append({"type": "text", "text": prompt})
    response = client.chat.completions.create(
        model=model_name,
        stream=False,
        messages=[{"role": "user", "content": content_list}],
    )
    score = response.choices[0].message.content.strip()
    return video_name_prefix, score


def process_video(video_path, api_key, model_name=None, base_url=None):
    video_prefix = os.path.splitext(os.path.basename(video_path))[0]
    try:
        frames = extract_frames(video_path)
        frames_base64 = [image_to_base64(f) for f in frames]
        return call_gpt(
            frames_base64,
            video_prefix,
            api_key=api_key,
            model_name=model_name,
            base_url=base_url,
        )
    except Exception as e:
        print(f"Failed processing {video_path}: {e}")
        return video_prefix, "error"


def process_video_threaded(
    file_path, result_dict, api_key, model_name=None, base_url=None
):
    video_key, score = process_video(file_path, api_key, model_name, base_url)
    result_dict[video_key] = score


def process_folder(
    input_video_folder,
    output_json_file,
    num_workers,
    api_key,
    model_name=None,
    base_url=None,
):
    print(f"Processing folder: {input_video_folder}")

    video_files = [f for f in os.listdir(input_video_folder) if f.endswith(".mp4")]

    result_dict = {}
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for f in tqdm(
            video_files, desc=f"Processing {os.path.basename(input_video_folder)}"
        ):
            full_path = os.path.join(input_video_folder, f)
            futures.append(
                executor.submit(
                    process_video_threaded,
                    full_path,
                    result_dict,
                    api_key,
                    model_name,
                    base_url,
                )
            )

        for future in as_completed(futures):
            future.result()

    with open(output_json_file, "w") as f:
        json.dump(result_dict, f, indent=4)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_video_folder",
        type=str,
        default="demo_result/model_name_input_video",
    )
    parser.add_argument(
        "--output_json_folder",
        type=str,
        default="demo_result/model_name_output_json/",
    )
    parser.add_argument("--api_key", type=str, default=None)
    parser.add_argument("--model_name", type=str, default="gpt-4o-2024-11-20")
    parser.add_argument("--base_url", type=str, default=None)
    parser.add_argument("--num_workers", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()

    input_video_folder = args.input_video_folder
    output_json_folder = args.output_json_folder
    api_key = args.api_key
    model_name = args.model_name
    base_url = args.base_url
    num_workers = args.num_workers

    os.makedirs(output_json_folder, exist_ok=True)

    for i in [1, 2, 3]:
        output_json_file = os.path.join(output_json_folder, f"naturalscore_{i}.json")
        if not os.path.exists(output_json_file):
            process_folder(
                input_video_folder,
                output_json_file,
                num_workers,
                api_key,
                model_name,
                base_url,
            )
        else:
            print(f"{output_json_file}: continue")

    print(f"All results have been saved to {output_json_folder}")


if __name__ == "__main__":
    main()
