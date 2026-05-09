## Why

Actualmente las fotos periódicas de referencia (museo) y las evidencias de detección se guardan en directorios separados (`museum/` y `detections/`) con formatos de nombre inconsistentes entre sí. Esto dificulta reconstruir la cronología: para saber qué aspecto tenía la escena antes de una detección hay que buscar en dos carpetas con convenciones distintas. Unificar todo en `photo_historic/` con un formato de nombre homogéneo permite correlacionar cualquier evento con su contexto fotográfico previo con una sola vista.

## What Changes

- **BREAKING** Todas las imágenes (museo y detecciones) pasan a guardarse en `photo_historic/YYYY-MM-DD/` en lugar de `museum/YYYY-MM-DD/` y `detections/`.
- **BREAKING** El formato de nombre de fichero se unifica a `YYYY-MM-DD-HH-MM-SS_{type}.jpg` para todos los tipos:
  - `..._museum` — frame periódico de referencia (antes sin sufijo de tipo).
  - `..._detection` — evidencia de detección confirmada (antes `YYYYMMDD_HHMMSS_mmm_detection.jpg`).
  - `..._desechada_double` — descartado por múltiples blobs (antes mismo formato que detección).
  - `..._fondo_cambiado` — descartado por evento fotométrico (antes mismo formato que detección).
- **BREAKING** `config.yaml` consolida `storage.output_dir` y `museum.output_dir` en una única clave `photo_historic.output_dir`.
- El módulo `src/storage/__init__.py` adopta el nuevo formato de nombre y directorio.
- El módulo `src/storage/museum.py` adopta el mismo formato de nombre con sufijo `_museum` y usa `photo_historic.output_dir`.
- El `orchestrator` pasa `config['photo_historic']['output_dir']` a ambos módulos de almacenamiento.

## Capabilities

### New Capabilities

*(ninguna — solo cambios a capacidades existentes)*

### Modified Capabilities

- `jpeg-storage`: **BREAKING** nuevo directorio `photo_historic/YYYY-MM-DD/` y nuevo formato de nombre `YYYY-MM-DD-HH-MM-SS_{type}.jpg` (sustituye al formato `YYYYMMDD_HHMMSS_mmm_{prefix}.jpg` en `detections/`).
- `museum-storage`: **BREAKING** nuevo directorio `photo_historic/YYYY-MM-DD/` compartido con `jpeg-storage`, nuevo formato de nombre `YYYY-MM-DD-HH-MM-SS_museum.jpg` (sustituye a `YYYY-MM-DD_HH-MM-SS.jpg` en `museum/`).
- `config-and-entrypoint`: **BREAKING** clave `storage.output_dir` y `museum.output_dir` se eliminan y se sustituyen por `photo_historic.output_dir`.

## Impact

- `src/storage/__init__.py` — cambia la generación del nombre de fichero y la estructura de subdirectorios.
- `src/storage/museum.py` — cambia el nombre de fichero generado; el directorio de destino pasa a ser `photo_historic/`.
- `src/orchestrator/__init__.py` — usa `config['photo_historic']['output_dir']` para ambas llamadas de almacenamiento.
- `config.yaml` — se elimina `storage.output_dir` y `museum.output_dir`; se añade `photo_historic.output_dir`.
- La carpeta `detections/` y `museum/` dejan de recibir nuevos ficheros tras el cambio; pueden archivarse o eliminarse manualmente.
- No hay cambios en `src/detector/`, `src/capture/` ni `src/publisher/`.
