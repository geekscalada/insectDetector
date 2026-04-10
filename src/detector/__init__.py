from dataclasses import dataclass

import cv2
import numpy as np


@dataclass
class Detection:
    bbox: tuple  # (x, y, w, h)
    area: float
    aspect_ratio: float


_mog2 = None
_kernel = None
_cfg = None
_frame_count = 0
_morph_op = None

_MORPH_OPS = {
    'open':   cv2.MORPH_OPEN,
    'close':  cv2.MORPH_CLOSE,
    'erode':  cv2.MORPH_ERODE,
    'dilate': cv2.MORPH_DILATE,
}


def init(config: dict) -> None:
    global _mog2, _kernel, _cfg, _frame_count, _morph_op
    _cfg = config
    _mog2 = cv2.createBackgroundSubtractorMOG2(
        history=config['mog2_history'],
        varThreshold=config['mog2_var_threshold'],
        detectShadows=bool(config['detect_shadows']),
    )
    _mog2.setShadowThreshold(config['mog2_shadow_threshold'])
    _kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (config['morph_kernel_size'], config['morph_kernel_size']),
    )
    _morph_op = _MORPH_OPS[config['morph_operator']]
    _frame_count = 0


def detect(frame: np.ndarray) -> list:
    global _frame_count
    mask = _mog2.apply(frame)
    _frame_count += 1
    if _frame_count <= _cfg['warmup_frames']:
        return []

    _, fg_mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

    iterations = _cfg['morph_iterations']
    fg_mask = cv2.morphologyEx(fg_mask, _morph_op, _kernel, iterations=iterations)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    for c in contours:
        area = cv2.contourArea(c)
        if not (_cfg['min_area'] <= area <= _cfg['max_area']):
            continue
        x, y, w, h = cv2.boundingRect(c)
        if min(w, h) == 0:
            continue
        aspect_ratio = max(w, h) / min(w, h)
        if not (_cfg['min_aspect_ratio'] <= aspect_ratio <= _cfg['max_aspect_ratio']):
            continue
        detections.append(Detection(bbox=(x, y, w, h), area=area, aspect_ratio=aspect_ratio))

    return detections


def annotate(frame: np.ndarray, detections: list) -> np.ndarray:
    out = frame.copy()
    for d in detections:
        x, y, w, h = d.bbox
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return out
