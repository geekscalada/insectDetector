## Context

El módulo `detector` ya devuelve objetos `Detection` con `bbox: tuple[int,int,int,int]` (x,y,w,h). El módulo `storage` guarda el frame tal cual lo recibe. El orchestrator tiene acceso tanto al frame como a la lista de detecciones en el momento de la llamada a `storage.save`. Actualmente ese frame no lleva ninguna anotación visual.

El proyecto sigue una separación estricta: el orchestrator cablea módulos pero no implementa lógica CV propia. Cualquier operación OpenCV debe vivir en el módulo `detector`.

## Goals / Non-Goals

**Goals:**
- Guardar el frame con el bounding box de cada detección dibujado.
- Mantener los contratos de `detector.detect` y `storage.save` sin cambiar sus firmas.
- No añadir parámetros nuevos a `config.yaml`.

**Non-Goals:**
- Dibujado de texto, etiquetas, área ni aspect ratio sobre el frame (MVP).
- Configuración dinámica del color o grosor del rectángulo.
- Anotación de frames sin detecciones (si `detections` está vacía, se devuelve el frame original sin copiar innecesariamente).

## Decisions

### D1 — `annotate()` vive en `src/detector/`

**Decisión:** la función `annotate(frame, detections)` se añade al módulo `detector`.

**Alternativas descartadas:**
- *Orchestrator*: violaría "el orchestrator no hace CV directo".
- *Nuevo módulo `src/annotator/`*: sobre-ingeniería para una sola función.
- *`storage`*: el módulo storage no debe contener lógica CV.

`detector` ya importa OpenCV y ya define `Detection`. Es el lugar natural.

### D2 — `annotate()` devuelve una copia del frame

**Decisión:** `frame.copy()` antes de dibujar, devolviendo el frame anotado sin mutar el original.

**Rationale:** evita efectos secundarios si el bucle reutilizara el frame original en otra operación (p.ej. en una iteración futura del modelo MOG2).

### D3 — Estilo visual fijo como constante interna

**Decisión:** color `(0, 255, 0)` (verde BGR) y grosor `2` definidos como constantes dentro de `annotate()`, sin exponer parámetros nuevos en `config.yaml`.

**Rationale:** el color del rectángulo no es un parámetro de algoritmo; cambiarlo no afecta a la detección. Añadirlo a la configuración añadiría ruido sin valor para el MVP.

### D4 — Punto de integración en el orchestrator

**Decisión:** el orchestrator llama `annotate(frame, detections)` entre `detect()` y `storage.save()`:

```python
detections = detector.detect(frame)
if detections and cooldown_ok:
    annotated = detector.annotate(frame, detections)
    storage.save(annotated, timestamp)
    publisher.publish(payload)
```

El frame original nunca se modifica; `storage.save` recibe el frame anotado.

## Risks / Trade-offs

- **[Riesgo] Overhead de `.copy()`** → El frame es un array BGR de resolución de captura (~640×480×3 ≈ 900 KB). La copia ocurre sólo en eventos (no en cada frame), por lo que el coste es despreciable.
- **[Riesgo] Bounding boxes incorrectos si `bbox` está en coordenadas relativas** → Los `bbox` de `detector.detect` ya son coordenadas absolutas en píxeles (x,y,w,h), directamente usables con `cv2.rectangle`. Sin riesgo.
- **[Trade-off] Evidencias ya guardadas no se pueden retroactivamente anotar** → Decisión de diseño: aceptado. Sólo las nuevas capturas tendrán anotaciones.

## Migration Plan

1. Añadir `annotate()` en `src/detector/`.
2. Actualizar el orchestrator para llamar a `annotate` antes de `storage.save`.
3. No se requiere migración de datos ni rollback especial — si se revierte el cambio, las capturas vuelven a ser frames en crudo.

## Open Questions

Ninguna. El cambio es autocontenido y no tiene dependencias externas ni decisiones pendientes.
