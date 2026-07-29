import numpy as np

def calculate_akd(pred_kps, gt_kps, visibility=None):
    """
    Calculate Average Keypoint Distance (AKD).
    pred_kps: (N, K, 2) or (K, 2)
    gt_kps: (N, K, 2) or (K, 2)
    visibility: (N, K) or (K,) - Confidence scores. Only calc for vis > 0.
    """
    # Safety checks for None inputs
    if pred_kps is None:
        # print("Debug: pred_kps is None in calculate_akd")
        return None
    if gt_kps is None:
        # print("Debug: gt_kps is None in calculate_akd")
        return None

    diff = pred_kps - gt_kps
    dist = np.linalg.norm(diff, axis=-1) # (N, K)
    
    if visibility is not None:
        mask = visibility > 0
        if np.sum(mask) == 0:
            return 0.0
        return np.sum(dist * mask) / np.sum(mask)
    else:
        return np.mean(dist)

def calculate_pck(pred_kps, gt_kps, threshold=0.05, visibility=None, head_size=None):
    """
    Calculate Percentage of Correct Keypoints (PCK).
    pred_kps: (N, K, 2)
    gt_kps: (N, K, 2)
    threshold: fraction of bounding box size or head size.
    head_size: (N,) - used for normalization (PCKh).
    """
    if pred_kps is None or gt_kps is None:
        return None

    diff = pred_kps - gt_kps
    dist = np.linalg.norm(diff, axis=-1) # (N, K)
    
    if head_size is not None:
        # Normalize by head size (PCKh)
        thresh_val = threshold * head_size[:, None] # (N, 1)
    else:
        thresh_val = threshold # Scalar (pixels)

    correct = dist <= thresh_val
    
    if visibility is not None:
        mask = visibility > 0
        if np.sum(mask) == 0:
            return 0.0
        return np.sum(correct * mask) / np.sum(mask)
    else:
        return np.mean(correct)

def split_keypoints(kps, scores=None):
    """
    Split 133 COCO-WholeBody keypoints into Body(NoFace) and Hand.
    Handles 134-point DWPose format (Index 0 is Root) by shifting.
    
    Returns:
        body_kps, hand_kps, body_scores, hand_scores
    """
    if kps is None:
        return None, None, None, None

    # Define indices
    # Body + Foot: 0-23
    # Face: 23-91 (Exclude from evaluation)
    # Hands: 91-133
    
    idx_body = list(range(0, 23))
    idx_hand = list(range(91, 133))
    
    # Check shape
    # Support (N, 134, 2) or (134, 2)
    # The last dimension is coordinates (2 or 3), the second to last is keypoints
    dim_idx = -2 
    
    if kps.shape[dim_idx] == 134:
        # User info: "In 134-point array, the extra point (root) is usually at index 0"
        # So we need to shift all indices by 1
        # print(f"Debug: Detected 134 points (DWPose with Root). Input shape: {kps.shape}. Shifting indices.")
        idx_body = [i + 1 for i in idx_body]
        idx_hand = [i + 1 for i in idx_hand]
    elif kps.shape[dim_idx] == 133:
        # Standard COCO-WholeBody
        pass
    else:
        print(f"Warning: Keypoints shape {kps.shape} does not match 133 or 134. Using all as body. Hands will be None.")
        return kps, None, scores, None

    # Slice the data
    kps_body = kps[..., idx_body, :]
    kps_hand = kps[..., idx_hand, :]
    
    scores_body = scores[..., idx_body] if scores is not None else None
    scores_hand = scores[..., idx_hand] if scores is not None else None
    
    return kps_body, kps_hand, scores_body, scores_hand
