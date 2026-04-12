import os
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


def save(frame: np.ndarray, timestamp: datetime, output_dir: str, prefix: str = "detection") -> Path:
    os.makedirs(output_dir, exist_ok=True)
    ts = timestamp.strftime("%Y%m%d_%H%M%S_") + f"{timestamp.microsecond // 1000:03d}"
    filename = f"{ts}_{prefix}.jpg"
    filepath = Path(output_dir) / filename
    cv2.imwrite(str(filepath), frame)
    return filepath
