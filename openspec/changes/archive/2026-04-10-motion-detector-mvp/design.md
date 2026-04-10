## Context

El sistema tiene capture y storage funcionales y verificados en hardware. El orchestrator actual ejecuta un bucle limitado (`capture_limit`) que guarda todos los frames incondicionalmente — no hay filtrado de movimiento. Este cambio introduce el detector como núcleo del sistema y adapta el orchestrator para funcionar en modo continuo real.

Módulos afectados: `src/detector/` (nuevo), `src/orchestrator/` (refactorizado), `config.yaml` (actualizado).

## Goals / Non-Goals

**Goals:**
- Implementar `detect(frame) → list[Detection]` con MOG2 + morfología + filtros de área y aspect ratio.
- El orchestrator pasa a bucle continuo (sin `capture_limit`), guarda solo cuando hay detecciones válidas y el cooldown ha expirado.
- `config.yaml` refleja todos los parámetros del detector como única fuente de verdad.

**Non-Goals:**
- No se implementa publisher MQTT en este cambio.
- No se añade gestión de almacenamiento (límite de disco, rotación).
- No se modifica la interfaz de `capture` ni `storage`.
- No se añade UI ni modo de debug visual.

## Decisions

### D1: MOG2 con `detectShadows=True` y umbralización a 255

**Decisión:** Usar `detectShadows=True` y filtrar la máscara con `cv2.threshold(mask, 254, 255, THRESH_BINARY)` para descartar los píxeles de sombra (127).

**Alternativa considerada:** `detectShadows=False` — más rápido, pero deja pasar sombras de personas como falsos positivos. Es el mayor fuente de FP en una cámara cenital. Descartado.

### D2: Pipeline erosión → dilatación con kernel elíptico

**Decisión:** `cv2.erode` seguido de `cv2.dilate` con `MORPH_ELLIPSE`. La erosión elimina ruido de un píxel; la dilatación reune fragmentos de blobs de insectos rápidos que MOG2 divide en contornos separados.

**Alternativa considerada:** Solo dilatación — no limpia el ruido inicial. Solo erosión — puede destruir blobs pequeños. El pipeline combinado es el equilibrio correcto.

### D3: Filtro área + aspect ratio como discriminador principal

**Decisión:** Doble filtro: área en rango [min_area, max_area] y aspect ratio (max(w,h)/min(w,h)) en rango [min_aspect_ratio, max_aspect_ratio]. Cockroaches son alargadas (ratio ~1.5–3.0); personas vistas desde el techo son casi circulares (~1.0–1.2).

**Alternativa considerada:** Solo filtro de área — insuficiente, una mano o pie puede estar en el rango de área. El aspect ratio es el discriminador clave. Descartado como único filtro.

### D4: MOG2 instanciado en el módulo detector (estado interno)

**Decisión:** El objeto `mog2` se crea una vez dentro del módulo detector y `detect()` lo actualiza en cada llamada. El estado del modelo de fondo es persistente a lo largo de la vida del proceso.

**Alternativa considerada:** Pasar el objeto mog2 como parámetro desde el orchestrator — añade complejidad de inicialización sin beneficio para este MVP. Descartado.

### D5: Warm-up de MOG2 (primeros N frames sin detecciones)

**Decisión:** El detector descarta detecciones durante los primeros `warmup_frames` (≈50) para evitar falsos positivos mientras MOG2 construye el modelo de fondo inicial. El contador de warm-up es estado interno del detector.

**Alternativa considerada:** Confiar en que el operador no haya movimiento durante el arranque — no contralable en producción. Descartado.

### D6: El orchestrator refactorizado usa SIGTERM/KeyboardInterrupt para terminar

**Decisión:** El bucle continuo se detiene con `Ctrl+C` (KeyboardInterrupt) o SIGTERM. No hay `capture_limit`. La lógica de cooldown (60s entre guardados) se implementa con `datetime.now()` y `last_saved_at`.

**Alternativa considerada:** Timeout configurable — añade un parámetro más a config sin necesidad real en hardware dedicado. Descartado para MVP.

## Risks / Trade-offs

- **Warm-up visible en arranque** → Durante ~5 segundos (50 frames a 10 FPS) no hay detecciones. Aceptable; el sistema no funciona en tiempo real estricto.
- **CPU Pi 4 con MOG2 a 640×480 10 FPS** → Dentro de límites seguros según benchmarks documentados en el skill opencv-raspi-patterns. Monitorizar en hardware si hay regresión.
- **Estado interno del detector (mog2)** → Impide instanciar múltiples detectores en el mismo proceso sin conflicto. No es un caso de uso del MVP.
- **capture_limit eliminado es BREAKING** → Cualquier script de test o integración que pase `capture_limit` en config dejará de tenerlo en cuenta. Los tests existentes del orchestrator basados en el spec antiguo deberán actualizarse.

## Migration Plan

1. Añadir parámetros del detector a `config.yaml` real (si no están ya).
2. Eliminar `orchestrator.capture_limit` de `config.yaml`.
3. Implementar `src/detector/__init__.py`.
4. Refactorizar `src/orchestrator/__init__.py`.
5. Verificar manualmente con frames sintéticos en entorno de desarrollo.
6. Verificar en hardware Raspberry Pi con cámara real.

No hay migración de datos: los JPEGs existentes en `detections/` no se ven afectados.

## Open Questions

- ¿Cuántos `warmup_frames` son suficientes en el entorno real? El valor de 50 es orientativo; puede necesitar ajuste tras prueba en hardware.
- ¿Se añade `orchestrator.warmup_frames` a config.yaml o se deja como constante interna? (Recomendación: añadirlo a config para facilitar ajuste en campo sin tocar código.)
