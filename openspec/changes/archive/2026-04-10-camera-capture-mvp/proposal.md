## Why

No hay ninguna línea de código ejecutable todavía. Antes de invertir tiempo en el pipeline completo de detección, necesitamos verificar en hardware real que picamera2 funciona, que los frames llegan con la forma y tipo esperados, y que el bucle de captura es estable. Este MVP da esa confirmación observable: tú ves los JPEGs guardados en `detections/`.

## What Changes

- Implementar `src/capture/` con un `FrameSource` (generador) que entrega frames BGR a 10 FPS usando picamera2
- Implementar `src/storage/` con `save(frame, timestamp) -> Path` que escribe JPEGs en `detections/`
- Implementar `src/orchestrator/` con `run(config)` que ejecuta un bucle limitado: captura N frames (configurable, por defecto 5), guarda cada uno, y termina
- Actualizar `config.yaml` con el parámetro `capture_limit` bajo la sección `orchestrator`

## Capabilities

### New Capabilities

- `frame-capture`: El módulo `capture` entrega frames BGR desde la Camera Module 2 NoIR via picamera2 a la frecuencia configurada
- `jpeg-storage`: El módulo `storage` persiste un frame numpy como JPEG con timestamp en `detections/`
- `capture-loop`: El `orchestrator` ejecuta un bucle de captura limitado que integra `capture` y `storage`, termina limpiamente tras N frames

### Modified Capabilities

- `config-and-entrypoint`: Se añade el parámetro `orchestrator.capture_limit` a `config.yaml`

## Impact

- `src/capture/__init__.py`: se implementa por primera vez
- `src/storage/__init__.py`: se implementa por primera vez
- `src/orchestrator/__init__.py`: se implementa por primera vez (versión limitada MVP)
- `config.yaml`: nueva clave `orchestrator.capture_limit`
- `main.py`: sin cambios — ya delega a `orchestrator.run(config)`
- `src/detector/__init__.py`, `src/publisher/__init__.py`: sin cambios — no se usan en este MVP
