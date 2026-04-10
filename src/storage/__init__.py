import os
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


def save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path:
    os.makedirs(output_dir, exist_ok=True)
    filename = timestamp.strftime("%Y-%m-%dT%H-%M-%S.") + f"{timestamp.microsecond:06d}.jpg"
    filepath = Path(output_dir) / filename
    cv2.imwrite(str(filepath), frame)
    return filepath
