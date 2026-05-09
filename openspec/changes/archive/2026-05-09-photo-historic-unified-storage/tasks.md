## 1. Configuración

- [x] 1.1 En `config.yaml`: eliminar `storage.output_dir`, eliminar `museum.output_dir` y añadir sección `photo_historic` con clave `output_dir: photo_historic/` y los comentarios de documentación correspondientes.

## 2. Módulo `src/storage/__init__.py`

- [x] 2.1 Cambiar la generación del nombre de fichero en `save()` al formato `YYYY-MM-DD-HH-MM-SS_{prefix}.jpg` (sin milisegundos, dashes uniformes en fecha y hora).
- [x] 2.2 Añadir creación del subdirectorio de día `output_dir/YYYY-MM-DD/` y guardar el fichero en ese subdirectorio.

## 3. Módulo `src/storage/museum.py`

- [x] 3.1 Cambiar la generación del nombre de fichero en `save()` al formato `YYYY-MM-DD-HH-MM-SS_museum.jpg` (en lugar de `YYYY-MM-DD_HH-MM-SS.jpg`).

## 4. Módulo `src/orchestrator/__init__.py`

- [x] 4.1 Sustituir `config['storage']['output_dir']` por `config['photo_historic']['output_dir']` en todas las llamadas a `storage.save()`.
- [x] 4.2 Sustituir `config['museum']['output_dir']` por `config['photo_historic']['output_dir']` en la llamada a `museum_storage.purge()` y en la llamada a `museum_storage.save()`.

## 5. Verificación manual

- [x] 5.1 Arrancar el sistema y confirmar que `photo_historic/YYYY-MM-DD/` se crea y recibe los frames de museo con el formato `YYYY-MM-DD-HH-MM-SS_museum.jpg`.
- [x] 5.2 Provocar una detección (o simular con `debug.py`) y confirmar que los ficheros de evidencia (`_detection`, `_desechada_double`, `_fondo_cambiado`) se crean en `photo_historic/YYYY-MM-DD/` con el nuevo formato.
- [x] 5.3 Confirmar que `museum/` y `detections/` no reciben nuevos ficheros tras el cambio.
