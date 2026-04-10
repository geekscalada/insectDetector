from datetime import datetime, timedelta

from src.capture import FrameSource
from src import detector, storage


def run(config: dict) -> None:
    fps = config['camera']['fps']
    output_dir = config['storage']['output_dir']
    cooldown_seconds = config['mqtt']['cooldown_seconds']

    detector.init(config['detector'])
    last_saved_at = None

    try:
        for frame in FrameSource(fps):
            detections = detector.detect(frame)
            if not detections:
                continue

            now = datetime.now()
            if last_saved_at is not None and (now - last_saved_at).total_seconds() < cooldown_seconds:
                continue

            try:
                annotated = detector.annotate(frame, detections)
                storage.save(annotated, now, output_dir)
                last_saved_at = now
            except Exception as e:
                print(f"storage error: {e}")
    except KeyboardInterrupt:
        print("Stopping.")
