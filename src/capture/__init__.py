from typing import Generator
import numpy as np


def FrameSource(camera_config: dict) -> Generator[np.ndarray, None, None]:
    from picamera2 import Picamera2  # deferred — only fails on instantiation
    cam = Picamera2()
    config = cam.create_video_configuration(
        main={"size": (camera_config['width'], camera_config['height']), "format": "BGR888"},
        controls={"FrameRate": float(camera_config['fps'])},
    )
    cam.configure(config)

    fixed_controls = {}
    if 'exposure_time' in camera_config:
        fixed_controls['ExposureTime'] = int(camera_config['exposure_time'])
    if 'analogue_gain' in camera_config:
        fixed_controls['AnalogueGain'] = float(camera_config['analogue_gain'])
    if camera_config.get('awb_enable') is False:
        fixed_controls['AwbEnable'] = False
    if fixed_controls:
        cam.set_controls(fixed_controls)

    cam.start()
    try:
        while True:
            yield cam.capture_array()
    finally:
        cam.stop()
        cam.close()
