from datetime import datetime

from src.capture import FrameSource
from src import storage


def run(config: dict) -> None:
    fps = config['camera']['fps']
    output_dir = config['storage']['output_dir']
    capture_limit = config['orchestrator']['capture_limit']

    for i, frame in enumerate(FrameSource(fps)):
        if i >= capture_limit:
            break
        try:
            storage.save(frame, datetime.now(), output_dir)
        except Exception as e:
            print(f"storage error on frame {i}: {e}")
