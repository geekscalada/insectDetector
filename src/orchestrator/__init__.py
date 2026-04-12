from datetime import datetime, timedelta

from src.capture import FrameSource
from src import detector, storage


def run(config: dict) -> None:
    output_dir = config['storage']['output_dir']
    cooldown_seconds = config['mqtt']['cooldown_seconds']

    detector.init(config['detector'])
    last_saved_at = None

    try:
        for frame in FrameSource(config['camera']):
            now = datetime.now()
            detections = detector.detect(frame)

            if detector.last_photometric_event():
                try:
                    storage.save(frame, now, output_dir, prefix="fondo_cambiado")
                except Exception as e:
                    print(f"storage error: {e}")
                continue

            if not detections and detector.last_qualifying_count() == 0:
                continue

            if detector.last_qualifying_count() > 1:
                try:
                    storage.save(frame, now, output_dir, prefix="desechada_double")
                except Exception as e:
                    print(f"storage error: {e}")
                continue

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
