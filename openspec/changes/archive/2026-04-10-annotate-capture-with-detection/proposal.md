## Why

Actualmente las capturas JPEG guardadas son frames en crudo: al revisarlas no queda claro qué parte de la imagen disparó la detección. Dibujar el rectángulo delimitador (bounding box) del contorno detectado sobre el frame antes de guardarlo convierte cada evidencia en autoexplicativa, sin necesidad de reanalizar el vídeo.

## What Changes

- Se introduce una función `annotate(frame, detections)` que dibuja los bounding boxes de las detecciones sobre una copia del frame y devuelve el frame anotado.
- El orchestrator llama a `annotate` justo antes de `storage.save`, pasando el frame anotado en lugar del frame original.
- No cambia la firma de `storage.save` — sólo cambia el frame que recibe.
- No cambia la firma de `detector.detect` — las detecciones ya contienen los `bbox` necesarios.

## Capabilities

### New Capabilities
- `detection-annotation`: función `annotate(frame: np.ndarray, detections: list[Detection]) -> np.ndarray` que dibuja un rectángulo por detección sobre una copia del frame y lo devuelve.

### Modified Capabilities
- `capture-loop`: el orchestrator ahora llama a `annotate(frame, detections)` antes de `storage.save(annotated_frame, timestamp)`.

## Impact

- **`src/detector/`**: se añade `annotate()` al módulo (la CV lógica de dibujo vive donde ya vive el resto de CV).
- **`src/orchestrator/`**: una línea adicional entre `detect()` y `storage.save()`.
- **`config.yaml`**: sin cambios — no hay parámetros nuevos que configurar (color y grosor del rectángulo se fijan como constantes razonables).
- **Contrato `storage.save`**: sin cambio de firma.
- **Contrato `detector.detect`**: sin cambio de firma.
