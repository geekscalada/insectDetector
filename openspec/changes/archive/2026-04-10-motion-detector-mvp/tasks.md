## 1. Configuración

- [x] 1.1 Añadir parámetros `detector.*` a `config.yaml` (mog2_history, mog2_var_threshold, detect_shadows, morph_kernel_size, morph_iterations, min_area, max_area, min_aspect_ratio, max_aspect_ratio, warmup_frames)
- [x] 1.2 Eliminar `orchestrator.capture_limit` de `config.yaml`
- [x] 1.3 Verificar que `mqtt.cooldown_seconds` existe en `config.yaml` (si no, añadirlo)

## 2. Módulo detector

- [x] 2.1 Implementar `Detection` (dataclass o namedtuple) con campos `bbox`, `area`, `aspect_ratio` en `src/detector/__init__.py`
- [x] 2.2 Instanciar `cv2.createBackgroundSubtractorMOG2` con parámetros de config como estado interno del módulo
- [x] 2.3 Implementar `detect(frame: np.ndarray) -> list[Detection]`: aplicar MOG2, umbralizar máscara a 255 para descartar sombras
- [x] 2.4 Añadir pipeline morfológico erosión → dilatación con kernel elíptico de tamaño y iteraciones desde config
- [x] 2.5 Extraer contornos con `cv2.findContours` y filtrar por área [min_area, max_area]
- [x] 2.6 Filtrar contornos por aspect ratio `max(w,h)/min(w,h)` en rango [min_aspect_ratio, max_aspect_ratio]
- [x] 2.7 Implementar contador de warm-up interno: suprimir detecciones durante las primeras `warmup_frames` llamadas

## 3. Refactorización del orchestrator

- [x] 3.1 Eliminar la lógica de `capture_limit` del bucle en `src/orchestrator/__init__.py`
- [x] 3.2 Inicializar el módulo detector con `config['detector']` antes del bucle principal
- [x] 3.3 Llamar a `detector.detect(frame)` en cada iteración del bucle
- [x] 3.4 Implementar lógica de cooldown con `last_saved_at` y `datetime.now()` usando `mqtt.cooldown_seconds`
- [x] 3.5 Guardar frame con `storage.save` solo cuando `detect()` devuelve detecciones Y cooldown expirado
- [x] 3.6 Envolver el bucle en `try/except KeyboardInterrupt` para terminación limpia

## 4. Verificación

- [x] 4.1 Verificar `detect()` con frame sintético de fondo estático → devuelve `[]`
- [x] 4.2 Verificar `detect()` con un blob sintético en rango válido → devuelve exactamente una `Detection`
- [x] 4.3 Verificar `detect()` con blob de área fuera de rango → devuelve `[]`
- [x] 4.4 Verificar `detect()` con blob de aspect ratio ~1.0 (cuadrado) → devuelve `[]`
- [x] 4.5 Verificar que el orchestrator no guarda cuando `detect()` devuelve `[]`
- [x] 4.6 Verificar que el cooldown suprime guardados repetidos en frames consecutivos positivos
