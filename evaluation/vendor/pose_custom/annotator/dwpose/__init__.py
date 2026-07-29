# Openpose
# Original from CMU https://github.com/CMU-Perceptual-Computing-Lab/openpose
# 2nd Edited by https://github.com/Hzzone/pytorch-openpose
# 3rd Edited by ControlNet
# 4th Edited by ControlNet (added face and correct hands)

import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import torch
import numpy as np
from . import util
from .wholebody import Wholebody
from scipy.linalg import orthogonal_procrustes
# from scipy.spatial import Procrustes

def procrustes_analysis(X, Y):
    X_centered = X - np.mean(X, axis=0)
    Y_centered = Y - np.mean(Y, axis=0)
    
    norm_X = np.linalg.norm(X_centered)
    norm_Y = np.linalg.norm(Y_centered)
    scale = norm_Y / norm_X if norm_X > 0 else 1.0
    
    A = np.dot(X_centered.T, Y_centered)
    U, s, Vt = np.linalg.svd(A)
    R = np.dot(U, Vt)
    
    if np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = np.dot(U, Vt)
    
    transformed = scale * np.dot(X_centered, R) + np.mean(Y, axis=0)
    
    return transformed

def align_facial_landmarks(landmarks_a, landmarks_b):
    if landmarks_a.ndim == 3:
        landmarks_a = landmarks_a[0]
    if landmarks_b.ndim == 3:
        landmarks_b = landmarks_b[0]
    
    mtx2 = procrustes_analysis(landmarks_a, landmarks_b)
    
    if landmarks_a.shape[0] == 73:
        return mtx2.reshape(1, 73, 2)
    else:
        return mtx2

def draw_pose(pose, H, W):
    bodies = pose['bodies']

    if 'faces' in pose:
        faces = pose['faces']
    if 'hands' in pose:
        hands = pose['hands']
    candidate = bodies['candidate']
    subset = bodies['subset']
    canvas = np.zeros(shape=(H, W, 3), dtype=np.uint8)

    canvas = util.draw_bodypose(canvas, candidate, subset)
    if 'hands' in pose:
        canvas = util.draw_handpose(canvas, hands)
    if 'faces' in pose:
        canvas = util.draw_facepose(canvas, faces)

    return canvas


class DWposeDetector:
    def __init__(self,device='cuda:0'):

        self.pose_estimation = Wholebody(device=device)

    def __call__(self, oriImg, draw_face=True,ref_face=None,return_face=False,draw_hand=True):
        oriImg = oriImg.copy()
        H, W, C = oriImg.shape
        with torch.no_grad():
            candidate, subset = self.pose_estimation(oriImg)
            
            # if ref_face is not None:
            # only get one person
            candidate=candidate[0:1,:,:]
            subset=subset[0:1,:]

            nums, keys, locs = candidate.shape

            candidate[..., 0] /= float(W)
            candidate[..., 1] /= float(H)
            tmp_candidate=candidate.copy()
            tmp_subset=subset.copy()

            body = candidate[:,:18].copy()
            body = body.reshape(nums*18, locs)
            score = subset[:,:18]
            for i in range(len(score)):
                for j in range(len(score[i])):
                    if score[i][j] > 0.3:
                        score[i][j] = int(18*i+j)
                    else:
                        score[i][j] = -1

            un_visible = subset<0.3
            candidate[un_visible] = -1

            foot = candidate[:,18:24]
            # if return_face:
            #     b_selected = np.vstack([body[0:1], body[-4:]])
            #     ref_face_value = np.concatenate([candidate[:,24:92], b_selected.reshape(1, -1, 2)], axis=1)
            #     return ref_face_value
            faces = candidate[:,24:92]
            # faces=candidate[:,72:92] 
            if draw_face:
                if ref_face is not None:

                    b_selected = np.vstack([body[0:1], body[-4:]])
                    faces=np.concatenate([faces, b_selected.reshape(1, -1, 2)], axis=1)
                    faces_candidate = align_facial_landmarks(faces, ref_face)
                    faces=faces_candidate[:, :68, :]
                    body_extracted = faces_candidate[:, 68:, :].squeeze(0)
                    body[0] = body_extracted[0]
                    body[-4:] = body_extracted[1:]

            hands = candidate[:,92:113]
            hands = np.vstack([hands, candidate[:,113:]])
            # body=body[:12,:]
            # score=score[:,:12]
            bodies = dict(candidate=body, subset=score)
            if draw_face and draw_hand:
                pose = dict(bodies=bodies, hands=hands, faces=faces)
            elif draw_hand:
                pose = dict(bodies=bodies, hands=hands)
            else:
                pose = dict(bodies=bodies)
            if return_face:
                return draw_pose(pose, H, W), tmp_candidate, tmp_subset
            else:
                return draw_pose(pose, H, W)
