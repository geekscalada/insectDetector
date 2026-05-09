from datetime import datetime
from pathlib import Path

import cv2
import numpy as np


def save(frame: np.ndarray, timestamp: datetime, output_dir: str, prefix: str = "detection") -> Path:
    day_dir = Path(output_dir) / timestamp.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    filename = timestamp.strftime("%Y-%m-%d-%H-%M-%S") + f"_{prefix}.jpg"
    filepath = day_dir / filename
    cv2.imwrite(str(filepath), frame)
    return filepath
