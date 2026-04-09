from typing import Generator
import numpy as np


def FrameSource(fps: int) -> Generator[np.ndarray, None, None]:
    from picamera2 import Picamera2  # deferred — only fails on instantiation
    cam = Picamera2()
    config = cam.create_video_configuration(
        main={"size": (640, 480), "format": "BGR888"},
        controls={"FrameRate": float(fps)},
    )
    cam.configure(config)
    cam.start()
    try:
        while True:
            yield cam.capture_array()
    finally:
        cam.stop()
        cam.close()
