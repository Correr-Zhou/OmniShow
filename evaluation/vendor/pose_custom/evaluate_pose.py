import os
import sys
import argparse
import pandas as pd
import numpy as np
import pickle
import cv2
from tqdm import tqdm
import json
import torch

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pose_utils.metrics import calculate_akd, calculate_pck, split_keypoints

try:
    from annotator.dwpose import DWposeDetector
except ImportError:
    print("Warning: Could not import annotator.dwpose. Ensure you are in the correct environment.")
    DWposeDetector = None

def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

class PoseEvaluator:
    def __init__(self):
        try:
            from annotator.dwpose import DWposeDetector
            self.detector = DWposeDetector()
        except ImportError:
            print("Error: Could not import annotator.dwpose. Please ensure 'annotator' folder is in pose_custom/ or PYTHONPATH.")
            raise

    def extract_pose_from_video(self, video_path, sample_stride=2, resize_short_edge=720):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return None, None, None

        # Pre-read all frames
        all_frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            all_frames.append(frame)
        cap.release()
        
        total_frames = len(all_frames)
        if total_frames == 0:
            return None, None, None
            
        # Downsampling indices
        process_indices = list(range(0, total_frames, sample_stride))
        
        computed_results = {}

        for i in tqdm(process_indices, desc=f"Extracting {os.path.basename(video_path)}", leave=False):
            frame = all_frames[i]
            
            # Resize optimization
            h, w = frame.shape[:2]
            scale_x, scale_y = 1.0, 1.0
            frame_input = frame
            
            if resize_short_edge is not None and min(h, w) > resize_short_edge:
                if h < w:
                    new_h = resize_short_edge
                    new_w = int(w * (resize_short_edge / h))
                else:
                    new_w = resize_short_edge
                    new_h = int(h * (resize_short_edge / w))
                
                frame_input = cv2.resize(frame, (new_w, new_h))
                scale_x = w / new_w
                scale_y = h / new_h

            _, faces_np, score_np = self.detector(frame_input, draw_face=False, draw_hand=True, return_face=True)
            
            if faces_np is None:
                 faces_np = np.zeros((1, 133, 2)) # Default placeholder
                 score_np = np.zeros((1, 133))
            else:
                # Rescale coordinates back to original size
                if resize_short_edge is not None:
                    faces_np[..., 0] *= scale_x
                    faces_np[..., 1] *= scale_y

            computed_results[i] = (faces_np, score_np)
        
        # Sort and collect
        sorted_indices = sorted(computed_results.keys())
        
        if not sorted_indices:
             return None, None, None

        kps_out = []
        scores_out = []
        
        for idx in sorted_indices:
            faces, scores = computed_results[idx]
            # faces shape might be (1, 134, 2) or (M, 134, 2)
            # We take the first person (M=0)
            if faces is not None and len(faces) > 0:
                kps_out.append(faces[0])
                scores_out.append(scores[0])
            else:
                # Fallback empty
                kps_out.append(np.zeros((133, 2)))
                scores_out.append(np.zeros((133,)))
                
        return np.array(kps_out), np.array(scores_out), sorted_indices

    def resample_pose(self, pose_data, target_len):
        """
        Simple linear interpolation to align FPS/Length.
        """
        source_len = len(pose_data)
        if source_len == target_len:
            return pose_data
            
        source_idx = np.linspace(0, source_len - 1, source_len)
        target_idx = np.linspace(0, source_len - 1, target_len)
        
        flat_data = pose_data.reshape(source_len, -1)
        flat_resampled = np.zeros((target_len, flat_data.shape[1]))
        
        for i in range(flat_data.shape[1]):
            flat_resampled[:, i] = np.interp(target_idx, source_idx, flat_data[:, i])
            
        return flat_resampled.reshape(target_len, pose_data.shape[1], pose_data.shape[2])

    def evaluate(self, gen_video_path, gt_pkl_path, sample_stride=2, resize_short_edge=720):
        # 1. Load GT
        gt_data = load_pkl(gt_pkl_path)
        
        # Handle GT shapes
        if len(gt_data.shape) == 3:
            gt_kps = gt_data
        elif len(gt_data.shape) == 2:
            gt_kps = gt_data.reshape(-1, 133, 2)
        else:
            print(f"Warning: Unknown GT shape {gt_data.shape}")
            return None
        
        # 2. Extract Gen Pose (Downsampled)
        cap = cv2.VideoCapture(gen_video_path)
        if not cap.isOpened():
            return None
        total_gen_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        gen_kps, gen_scores, indices = self.extract_pose_from_video(
            gen_video_path, 
            sample_stride=sample_stride, 
            resize_short_edge=resize_short_edge
        )
        
        if gen_kps is None:
            return None

        # 3. Align GT to Original Video Timeline (if needed)
        # Resample GT to match the *original* video frame count first
        T_gt = len(gt_kps)
        if total_gen_frames != T_gt:
             gt_kps = self.resample_pose(gt_kps, total_gen_frames)
        
        # 4. Slice GT to match Downsampled Pred
        # Only take frames corresponding to 'indices'
        valid_indices = [i for i in indices if i < len(gt_kps)]
        
        gt_kps_sliced = gt_kps[valid_indices]
        
        # Align lengths if mismatch
        if len(valid_indices) < len(gen_kps):
            gen_kps = gen_kps[:len(valid_indices)]
            gen_scores = gen_scores[:len(valid_indices)]
        elif len(gen_kps) < len(valid_indices):
            gt_kps_sliced = gt_kps_sliced[:len(gen_kps)]

        # 5. Split Body/Hand
        # This will now handle 134 points correctly via updated metrics.py
        gen_body, gen_hand, score_body, score_hand = split_keypoints(gen_kps, gen_scores)
        gt_body, gt_hand, _, _ = split_keypoints(gt_kps_sliced, None)
        
        if gen_hand is None:
            print(f"Warning: gen_hand is None for {os.path.basename(gen_video_path)}. Shape was {gen_kps.shape}")
        if gt_hand is None:
            print(f"Warning: gt_hand is None for {os.path.basename(gen_video_path)}. Shape was {gt_kps_sliced.shape}")

        gen_max = np.max(gen_kps) if len(gen_kps) > 0 else 0
        gt_max = np.max(gt_kps_sliced) if len(gt_kps_sliced) > 0 else 0

        # Auto-detect normalized coordinates (0-1) vs Pixels
        # If max value is small (< 2.0), assume normalized
        is_normalized = (gen_max <= 2.0 and gt_max <= 2.0)
        
        if is_normalized:
            # If normalized, threshold=10 is too big (covers entire image). Use 0.05 instead.
            pck_thresh = 0.05
            # print(f"Detected normalized coordinates. Using PCK threshold {pck_thresh}")
        else:
            pck_thresh = 10.0
            
        # Check for Mismatch
        if (gen_max > 2.0 and gt_max <= 2.0) or (gen_max <= 2.0 and gt_max > 2.0):
             print(f"Warning: Coordinate scale mismatch! Gen Max={gen_max}, GT Max={gt_max}. Results will be wrong.")

        # 6. Calculate Metrics
        # calculate_akd/pck now have None checks
        akd_body = calculate_akd(gen_body, gt_body, visibility=score_body)
        akd_hand = calculate_akd(gen_hand, gt_hand, visibility=score_hand)
        
        pck_body = calculate_pck(gen_body, gt_body, threshold=pck_thresh, visibility=score_body)
        pck_hand = calculate_pck(gen_hand, gt_hand, threshold=pck_thresh, visibility=score_hand)
        
        return {
            "pose_akd_body": akd_body,
            "pose_pck_body": pck_body,
            "pose_akd_hand": akd_hand,
            "pose_pck_hand": pck_hand
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_csv", type=str, required=True)
    parser.add_argument("--video_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--col_pose", type=str, default="pose_points")
    parser.add_argument("--video_col", type=str, default="video_filename")
    parser.add_argument("--sample_stride", type=int, default=8, help="Frame downsampling stride")
    parser.add_argument("--resize_short_edge", type=int, default=720, help="Resize input for speedup")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    df = pd.read_csv(args.dataset_csv)
    
    try:
        evaluator = PoseEvaluator()
    except Exception as e:
        print(f"Failed to initialize PoseEvaluator: {e}")
        return

    results = []
    
    video_files = sorted([f for f in os.listdir(args.video_dir) if f.endswith(('.mp4', '.avi', '.mov'))])
    
    # Try to sort numerically if possible
    try:
        video_files.sort(key=lambda x: int(os.path.splitext(x)[0].split('_')[0]))
    except:
        pass

    for idx, row in tqdm(df.iterrows(), total=len(df)):
        if args.video_col in df.columns:
            vid_name = row[args.video_col]
            vid_path = os.path.join(args.video_dir, vid_name)
        else:
            if idx < len(video_files):
                vid_path = os.path.join(args.video_dir, video_files[idx])
            else:
                print(f"Warning: No video found for index {idx}")
                continue
        
        if not os.path.exists(vid_path):
            print(f"Warning: Video not found {vid_path}")
            continue

        gt_path = row.get(args.col_pose, None)
        if not gt_path or not os.path.exists(str(gt_path)):
            print(f"Warning: GT Pose not found for row {idx}: {gt_path}")
            continue
            
        try:
            metrics = evaluator.evaluate(
                vid_path, 
                str(gt_path), 
                sample_stride=args.sample_stride, 
                resize_short_edge=args.resize_short_edge
            )
            if metrics:
                res_row = {
                    "video_filename": os.path.basename(vid_path),
                    **metrics
                }
                results.append(res_row)
        except Exception as e:
            print(f"Error evaluating {vid_path}: {e}")
            import traceback
            traceback.print_exc()

    out_df = pd.DataFrame(results)
    out_path = os.path.join(args.output_dir, "pose_results.csv")
    out_df.to_csv(out_path, index=False)
    print(f"Saved pose results to {out_path}")

if __name__ == "__main__":
    main()
