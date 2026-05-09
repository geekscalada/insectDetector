## Why

Las fotos de detección registran *cuándo* el modelo disparó, pero no el contexto visual en los momentos sin detección. Sin un histórico de frames de referencia es imposible diagnosticar a posteriori por qué el modelo falló (falso positivo, falso negativo) o cómo cambió la escena iluminada a lo largo del día.

La cámara ya captura frames continuamente a 10 FPS para el detector. Guardar una foto de museo cada 5 segundos es simplemente llamar `cv2.imwrite()` sobre un frame que ya está en memoria — sin abrir una segunda instancia de cámara, sin captura adicional, sin coste de CPU relevante.

## What Changes

- El orchestrator dispara una captura de museo cada 5 segundos, independientemente de si hay detecciones.
- Los frames de museo se guardan en `museum/YYYY-MM-DD/YYYY-MM-DD_HH-mm-ss.jpg` (carpetas por día).
- Al arrancar, se purgan automáticamente las carpetas de museo con más de 3 días de antigüedad.
- Se añade una sección `museum` a `config.yaml` con `interval_seconds` y `retention_days`.

## Capabilities

### New Capabilities
- `museum-storage`: Escribe frames JPEG en `museum/YYYY-MM-DD/` con nombre de timestamp y purga carpetas con antigüedad superior a `retention_days`.
- `museum-snapshot`: Lógica de disparo periódico en el orchestrator basada en tiempo transcurrido. Reutiliza el frame ya disponible en cada iteración del bucle de detección (10 FPS) — sin segunda instancia de cámara ni captura adicional.

### Modified Capabilities
- `config-and-entrypoint`: Se añade la sección `museum` (`interval_seconds`, `retention_days`, `output_dir`) al esquema de `config.yaml`.
- `capture-loop`: El orchestrator debe comprobar en cada iteración si ha transcurrido `interval_seconds` desde la última captura de museo y, si es así, llamar a `museum_storage.save`.

## Impact

- **`src/storage/`**: nuevo submódulo o función `museum_storage.save(frame, timestamp, config)` — no altera `save()` existente.
- **`src/orchestrator/`**: añade estado `last_museum_ts` y la llamada condicional a `museum_storage.save`.
- **`config.yaml`**: nueva sección `museum`.
- **`main.py`**: sin cambios previstos.
- Sin dependencias nuevas (solo stdlib `datetime`, `pathlib`, `shutil` ya disponibles).
