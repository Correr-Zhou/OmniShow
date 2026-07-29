import os
import cv2
import numpy as np
from PIL import Image
import argparse
import json
import decord
from concurrent.futures import ThreadPoolExecutor, as_completed


def sample_video_frames(video_path, num_frames=None):
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


def compute_farneback_optical_flow(frames):
    prev_gray = cv2.cvtColor(np.array(frames[0]), cv2.COLOR_BGR2GRAY)
    flow_maps = []
    magnitudes = []
    angles = []
    images = []
    hsv = np.zeros_like(frames[0])
    hsv[..., 1] = 255

    for frame in frames[1:]:
        gray = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)
        flow_map = cv2.calcOpticalFlowFarneback(
            prev_gray,
            gray,
            flow=None,
            pyr_scale=0.5,
            levels=3,
            winsize=15,
            iterations=3,
            poly_n=5,
            poly_sigma=1.2,
            flags=0,
        )
        magnitude, angle = cv2.cartToPolar(flow_map[..., 0], flow_map[..., 1])
        hsv[..., 0] = angle * 180 / np.pi / 2
        hsv[..., 2] = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        flow_maps.append(flow_map)
        magnitudes.append(magnitude)
        angles.append(angle)
        images.append(bgr)
        prev_gray = gray
    return flow_maps, magnitudes, angles, images


def compute_lk_optical_flow(frames):
    maxCorners = 50
    feature_params = {
        "maxCorners": maxCorners,
        "qualityLevel": 0.3,
        "minDistance": 7,
        "blockSize": 7,
    }
    lk_params = {
        "winSize": (15, 15),
        "maxLevel": 2,
        "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
    }
    color = np.random.randint(0, 255, (maxCorners, 3))
    old_frame = frames[0]
    old_gray = cv2.cvtColor(np.array(old_frame), cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask=None, **feature_params)
    mask = np.zeros_like(old_frame)

    for frame in frames[1:]:
        frame_gray = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2GRAY)
        p1, st, err = cv2.calcOpticalFlowPyrLK(
            old_gray, frame_gray, p0, None, **lk_params
        )
        if p1 is not None:
            good_new = p1[st == 1]
            good_old = p0[st == 1]
        for i, (new, old) in enumerate(zip(good_new, good_old)):
            a, b = new.ravel()
            c, d = old.ravel()
            mask = cv2.line(
                mask, (int(a), int(b)), (int(c), int(d)), color[i].tolist(), 2
            )
        old_gray = frame_gray.copy()
        p0 = good_new.reshape(-1, 1, 2)
    return mask


def _downscale_maps(flow_maps, downscale_size: int = 16):
    return [
        cv2.resize(
            flow,
            (downscale_size, int(flow.shape[0] * (downscale_size / flow.shape[1]))),
            interpolation=cv2.INTER_AREA,
        )
        for flow in flow_maps
    ]


def _motion_score(flow_maps):
    average_flow_map = np.mean(np.array(flow_maps), axis=0)
    return np.mean(average_flow_map)


def process_video(video_path):
    frames = sample_video_frames(video_path, num_frames=None)

    farneback, _, _, _ = compute_farneback_optical_flow(frames)
    farneback = float(_motion_score(_downscale_maps(farneback)))
    lucas_kanade = float(_motion_score(compute_lk_optical_flow(frames)))

    return {
        "motion_fb": abs(farneback),
        "motion_lk": lucas_kanade,
    }


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
        default="demo_result/model_name_output_json",
    )
    parser.add_argument("--num_workers", type=int, default=32)
    return parser.parse_args()


def main():
    args = parse_args()

    input_video_folder = args.input_video_folder
    output_json_folder = args.output_json_folder
    num_workers = args.num_workers

    output_json_file = os.path.join(output_json_folder, "motion_amplitude.json")
    os.makedirs(output_json_folder, exist_ok=True)
    if os.path.exists(output_json_file):
        print("continue")
        return

    all_results = {}
    video_files = [f for f in os.listdir(input_video_folder) if f.endswith(".mp4")]

    def worker(filename):
        video_path = os.path.join(input_video_folder, filename)
        video_prefix = os.path.splitext(filename)[0]
        motion_scores = process_video(video_path)
        return video_prefix, motion_scores

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(worker, filename) for filename in video_files]
        for future in as_completed(futures):
            video_prefix, motion_scores = future.result()
            all_results[video_prefix] = motion_scores

    with open(output_json_file, "w") as f:
        json.dump(all_results, f, indent=4)

    print(f"All results have been saved to {output_json_file}")


if __name__ == "__main__":
    main()
