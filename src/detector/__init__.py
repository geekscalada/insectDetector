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
_prev_gray = None
_photometric_cfg = None
_last_had_detection = False
_photometric_event = False
_max_width_px = None
_max_height_px = None
_qualifying_count = 0

_MORPH_OPS = {
    'open':   cv2.MORPH_OPEN,
    'close':  cv2.MORPH_CLOSE,
    'erode':  cv2.MORPH_ERODE,
    'dilate': cv2.MORPH_DILATE,
}


def init(config: dict) -> None:
    global _mog2, _kernel, _cfg, _frame_count, _morph_op, _prev_gray, _photometric_cfg, _last_had_detection
    global _photometric_event, _max_width_px, _max_height_px, _qualifying_count
    _cfg = config
    _photometric_cfg = config.get('photometric', {'enable': False})
    _prev_gray = None
    _last_had_detection = False
    _photometric_event = False
    _qualifying_count = 0

    pixels_per_cm = config['pixels_per_cm']
    if pixels_per_cm <= 0:
        raise ValueError(f"pixels_per_cm must be positive, got {pixels_per_cm}")
    _max_width_px = config['max_width_cm'] * pixels_per_cm
    _max_height_px = config['max_height_cm'] * pixels_per_cm

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
    global _frame_count, _prev_gray, _last_had_detection, _photometric_event, _qualifying_count

    _photometric_event = False

    curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    learning_rate = -1  # default: OpenCV auto
    if _prev_gray is None:
        _prev_gray = curr_gray
    elif _photometric_cfg.get('enable', False):
        mean_diff = np.mean(np.abs(curr_gray.astype(float) - _prev_gray.astype(float)))
        if mean_diff > _photometric_cfg['max_mean_diff']:
            # Reset warmup so MOG2 re-learns the background under new conditions.
            # Update _prev_gray so that once the scene stabilises at the new level,
            # consecutive frames at that exposure stop triggering the photometric filter.
            _frame_count = 0
            _photometric_event = True
            _prev_gray = curr_gray
            blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
            _mog2.apply(blurred_frame, learningRate=0)
            _last_had_detection = False
            return []
        learning_rate = _photometric_cfg.get('learning_rate', -1)

    # If the previous frame had a detection, freeze background learning so
    # MOG2 does not incorporate the insect's position into the background model.
    if _last_had_detection:
        learning_rate = 0

    _prev_gray = curr_gray

    # Apply Gaussian blur to the frame before MOG2 to eliminate camera sensor noise
    blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
    mask = _mog2.apply(blurred_frame, learningRate=learning_rate)
    _frame_count += 1
    if _frame_count <= _cfg['warmup_frames']:
        return []

    _, fg_mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)

    iterations = _cfg['morph_iterations']
    fg_mask = cv2.morphologyEx(fg_mask, _morph_op, _kernel, iterations=iterations)

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections = []
    qualifying = 0
    min_solidity = _cfg.get('min_solidity', 0.0)
    for c in contours:
        area = cv2.contourArea(c)
        if area < _cfg['min_area']:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if min(w, h) == 0:
            continue
        qualifying += 1
        # Discard if BOTH dimensions exceed the physical size limits.
        if w > _max_width_px and h > _max_height_px:
            continue
        # Discard diffuse blobs (fabric wrinkles, noise clusters) by solidity.
        solidity = area / (w * h)
        if solidity < min_solidity:
            continue
        aspect_ratio = max(w, h) / min(w, h)
        detections.append(Detection(bbox=(x, y, w, h), area=area, aspect_ratio=aspect_ratio))

    _qualifying_count = qualifying
    _last_had_detection = len(detections) > 0
    return detections


def last_photometric_event() -> bool:
    return _photometric_event


def last_qualifying_count() -> int:
    """Number of blobs that passed min_area in the last detect() call, before size/solidity filters."""
    return _qualifying_count


def annotate(frame: np.ndarray, detections: list) -> np.ndarray:
    out = frame.copy()
    for d in detections:
        x, y, w, h = d.bbox
        cv2.rectangle(out, (x, y), (x + w, y + h), (0, 255, 0), 2)
    return out
