## Context

El sistema guarda dos tipos de imágenes: frames periódicos de referencia ("museo") en `museum/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS.jpg` y evidencias de detección en `detections/YYYYMMDD_HHMMSS_mmm_{type}.jpg`. Los dos módulos (`src/storage/__init__.py` y `src/storage/museum.py`) usan convenios de nombre distintos y directorios separados, lo que impide correlacionar visualmente el estado de la escena antes de una detección sin buscar en dos ubicaciones con formatos diferentes.

## Goals / Non-Goals

**Goals:**
- Directorio único `photo_historic/YYYY-MM-DD/` para todos los tipos de imagen.
- Formato de nombre unificado `YYYY-MM-DD-HH-MM-SS_{type}.jpg` para toda imagen escrita en disco.
- Consolidar `storage.output_dir` y `museum.output_dir` en una sola clave de configuración `photo_historic.output_dir`.
- Mantener la organización por subdirectorio de día (necesaria dado el volumen de frames de museo).

**Non-Goals:**
- No migrar ficheros existentes en `museum/` ni `detections/` — quedan huérfanos; el operador decide archivarlos o eliminarlos.
- No cambiar la lógica de detección, captura ni publicación MQTT.
- No introducir una política de retención diferenciada por tipo de imagen.
- No añadir milisegundos al nombre de fichero (el cooldown y el intervalo de museo son ≥ 1 s).

## Decisions

### D1 — Formato de nombre `YYYY-MM-DD-HH-MM-SS_{type}.jpg`
Dashes uniformes en la parte de fecha y hora (sin separador `T`, sin guiones bajos entre fecha y hora). El sufijo `_{type}` distingue el origen: `_museum`, `_detection`, `_desechada_double`, `_fondo_cambiado`. La ordenación lexicográfica es equivalente a la ordenación cronológica, lo que facilita la inspección manual.

### D2 — Subdirectorio de día `photo_historic/YYYY-MM-DD/`
A 5 s/frame, el museo genera ~17 280 ficheros/día. Un directorio plano sería inmanejable. Ambos módulos de almacenamiento escriben bajo el mismo subdirectorio de día, lo que agrupa cronológicamente todos los eventos.

### D3 — Consolidar clave de configuración en `photo_historic.output_dir`
Eliminar `storage.output_dir` y `museum.output_dir` para tener una única fuente de verdad de dónde van las imágenes. Los parámetros de comportamiento del museo (`interval_seconds`, `retention_days`) permanecen bajo la sección `museum` — su ámbito es la lógica de toma periódica, no la ruta de almacenamiento.

### D4 — Política de purga aplicada a `photo_historic/`
`museum_storage.purge` continuará eliminando subdirectorios de día cuyo nombre cumpla `YYYY-MM-DD` y sea anterior a `hoy - retention_days`. Al operar sobre `photo_historic/`, la purga afectará también a los JPEGs de detección de esa fecha, lo que es aceptable: la política de retención es global para el directorio histórico.

### D5 — Responsabilidades de módulo sin cambio
`src/storage/__init__.py` sigue siendo el módulo para frames de detección (detection, desechada_double, fondo_cambiado). `src/storage/museum.py` sigue siendo el módulo para frames periódicos de referencia. Solo cambia el directorio de destino y el nombre de fichero generado; las firmas de función no cambian.

## Risks / Trade-offs

| Riesgo / Trade-off | Mitigación |
|---|---|
| Ficheros huérfanos en `museum/` y `detections/` tras el deploy | Documentar en las tareas que el operador debe archivar o eliminar manualmente las carpetas antiguas. |
| La purga borra también evidencias de detección antiguas | Aceptado — política de retención unificada es una mejora explícita respecto al estado actual (detecciones nunca se purgaban). |
| Colisiones de nombre si se generan dos frames del mismo tipo en el mismo segundo | Improbable: el cooldown de detección es ≥ 1 s y el intervalo de museo es ≥ 5 s. No se añade lógica extra. |
| Herramientas externas (Home Assistant, scripts) que lean `detections/` o `museum/` | Se asume que no existen — verificar antes del deploy en producción. |
