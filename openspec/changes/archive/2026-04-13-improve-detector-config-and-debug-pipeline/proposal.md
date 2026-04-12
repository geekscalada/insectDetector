## Why

El detector actual genera falsos positivos y no está calibrado para los criterios físicos reales de detección (tamaño en cm), además de que la pipeline de debug no permite diagnosticar adecuadamente el comportamiento del sistema. Es necesario reajustar la configuración y la pipeline de debug de forma iterativa, con criterios de aceptación bien definidos, para obtener un sistema fiable antes de ponerlo en producción.

## What Changes

- **Eliminar el filtro de aspect ratio**: ya no se filtra por forma del contorno; cualquier forma (cuadrado, rectángulo, círculo) es válida. El único criterio geométrico es el tamaño físico.
- **Añadir filtro de tamaño físico en cm**: el sistema filtrará por dimensión física máxima (alto y/o ancho ≤ 5 cm) usando un parámetro de calibración `pixels_per_cm` en `config.yaml`.
- **Descartar detecciones múltiples**: cuando se detectan más de un objeto en el mismo frame, las detecciones se desechan pero se guarda una foto `desechada_double_XXXXX.jpg` para análisis.
- **Re-warmup en inestabilidad fotométrica**: cuando el filtro fotométrico detecta un cambio global, además de suprimir la detección, se resetea el contador de warmup para que MOG2 vuelva a aprender el fondo nuevo. Se guarda una foto `fondo_cambiado_XXXXX.jpg` para trazabilidad.
- **Pipeline de debug actualizada**: `debug.py` se actualiza para reflejar todos estos nuevos estados, guardar fotos categorizadas, y facilitar la calibración iterativa mostrando dimensiones físicas de los objetos detectados.

## Capabilities

### New Capabilities
- `physical-size-calibration`: parámetro `pixels_per_cm` en config y filtrado de contornos por dimensión física en cm (alto ≤ max_height_cm Y/O ancho ≤ max_width_cm)
- `multi-detection-discard`: cuando hay más de una detección válida en el frame, los resultados se desechan y se guarda foto `desechada_double_XXXXX.jpg`
- `photometric-warmup-reset`: cuando el filtro fotométrico se activa, se resetea el warmup de MOG2 y se guarda foto `fondo_cambiado_XXXXX.jpg`

### Modified Capabilities
- `motion-detection`: eliminar el filtro de aspect ratio; el criterio de forma ya no aplica
- `debug-pipeline`: actualizar para mostrar dimensiones físicas en annotations, guardar fotos categorizadas con los nuevos prefijos, y facilitar calibración visual iterativa

## Impact

- `src/detector/__init__.py`: eliminar aspect ratio filter, añadir physical size filter, añadir re-warmup en inestabilidad fotométrica
- `src/storage/__init__.py`: nuevo nombre de fichero para snapshots fotométricos y descartes dobles
- `src/orchestrator/__init__.py`: propagar nueva semántica de detección multi-objeto (descartar + guardar)
- `config.yaml`: añadir `pixels_per_cm`, `max_height_cm`, `max_width_cm`; eliminar o deprecar `min_aspect_ratio` y `max_aspect_ratio`
- `debug.py`: soporte para todos los nuevos tipos de imagen guardada y anotaciones de tamaño físico
