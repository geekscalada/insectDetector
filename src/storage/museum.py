import re
import shutil
from datetime import datetime, date, timedelta
from pathlib import Path

import cv2
import numpy as np

_DATE_DIR_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path:
    day_dir = Path(output_dir) / timestamp.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    filename = timestamp.strftime("%Y-%m-%d-%H-%M-%S") + "_museum.jpg"
    filepath = day_dir / filename
    cv2.imwrite(str(filepath), frame)
    return filepath


def purge(output_dir: str, retention_days: int) -> None:
    root = Path(output_dir)
    if not root.exists():
        return
    cutoff = date.today() - timedelta(days=retention_days)
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if not _DATE_DIR_RE.match(entry.name):
            continue
        try:
            dir_date = date.fromisoformat(entry.name)
        except ValueError:
            continue
        if dir_date < cutoff:
            shutil.rmtree(entry)
