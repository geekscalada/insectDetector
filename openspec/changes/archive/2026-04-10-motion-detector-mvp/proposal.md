## Why

El sistema actual captura frames y los guarda incondicionalmente — no distingue si hay un insecto o no. Sin el detector, no existe producto: el sistema llena disco y no notifica nada. Este es el cambio núcleo que convierte la infraestructura de captura en un detector de plagas funcional.

## What Changes

- **New**: `src/detector/__init__.py` — implementa `detect(frame) -> list[Detection]` con MOG2 + morfología + filtro de área y aspect ratio.
- **Modified**: `src/orchestrator/__init__.py` — se elimina `capture_limit`; el bucle pasa a ser continuo, guardando únicamente cuando `detect()` devuelve detecciones y el cooldown lo permite.
- **Modified**: `config.yaml` — se añaden/verifican los parámetros del detector (`mog2_history`, `mog2_var_threshold`, `detect_shadows`, `morph_kernel_size`, `morph_iterations`, `min_area`, `max_area`, `min_aspect_ratio`, `max_aspect_ratio`); se elimina `orchestrator.capture_limit`. **BREAKING**: `orchestrator.capture_limit` desaparece del config y del orchestrator.

## Capabilities

### New Capabilities

- `motion-detection`: Módulo detector que transforma un frame BGR en una lista de detecciones filtradas por área y aspect ratio usando MOG2 con sustracción de sombras y pipeline erosión-dilatación.

### Modified Capabilities

- `capture-loop`: El requisito de bucle limitado por `capture_limit` cambia a bucle continuo terminado por señal (Ctrl+C / SIGTERM). La lógica de guardado pasa de "guardar siempre" a "guardar solo con detecciones válidas y cooldown expirado".
- `config-and-entrypoint`: `orchestrator.capture_limit` se elimina del config; los parámetros del detector ya declarados en el spec se promueven al config real.

## Impact

- `src/detector/__init__.py` — fichero nuevo, módulo completo.
- `src/orchestrator/__init__.py` — refactorización del bucle principal.
- `config.yaml` — adición de parámetros detector, eliminación de `capture_limit`.
- No se toca `src/capture/`, `src/storage/`, `src/publisher/`, `main.py`.
- No hay nuevas dependencias de runtime (opencv-python-headless ya está en requirements.txt).
