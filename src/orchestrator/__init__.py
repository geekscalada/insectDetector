from datetime import datetime, timedelta

from src.capture import FrameSource
from src import detector, storage
from src.storage import museum as museum_storage


def run(config: dict) -> None:
    output_dir = config['photo_historic']['output_dir']
    cooldown_seconds = config['mqtt']['cooldown_seconds']

    detector.init(config['detector'])
    last_saved_at = None

    museum_storage.purge(config['photo_historic']['output_dir'], config['museum']['retention_days'])
    last_museum_ts = None

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
                pass
            elif detector.last_qualifying_count() > 1:
                try:
                    storage.save(frame, now, output_dir, prefix="desechada_double")
                except Exception as e:
                    print(f"storage error: {e}")
            elif last_saved_at is None or (now - last_saved_at).total_seconds() >= cooldown_seconds:
                try:
                    annotated = detector.annotate(frame, detections)
                    storage.save(annotated, now, output_dir)
                    last_saved_at = now
                except Exception as e:
                    print(f"storage error: {e}")

            if last_museum_ts is None or (now - last_museum_ts).total_seconds() >= config['museum']['interval_seconds']:
                try:
                    museum_storage.save(frame, now, config['photo_historic']['output_dir'])
                    last_museum_ts = now
                except Exception as e:
                    print(f"museum storage error: {e}")

    except KeyboardInterrupt:
        print("Stopping.")
