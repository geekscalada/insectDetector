## 1. Configuración — nuevos parámetros y eliminación de aspect ratio

- [x] 1.1 Añadir `pixels_per_cm`, `max_width_cm` y `max_height_cm` a `config.yaml` con documentación inline y valores iniciales razonables
- [x] 1.2 Eliminar `min_aspect_ratio` y `max_aspect_ratio` de `config.yaml` (o marcarlos como deprecados con comentario)

## 2. Módulo detector — physical size filter + eliminar aspect ratio

- [x] 2.1 En `detector.init()`, calcular y almacenar `_max_width_px` y `_max_height_px` desde `pixels_per_cm` × cm; añadir `ValueError` si `pixels_per_cm <= 0`
- [x] 2.2 En `detector.detect()`, eliminar el filtro de aspect ratio del bucle de contornos
- [x] 2.3 En `detector.detect()`, añadir el filtro físico: descartar contorno si `w > _max_width_px AND h > _max_height_px`

## 3. Módulo detector — photometric warmup reset + last_photometric_event()

- [x] 3.1 Añadir variable de módulo `_photometric_event: bool = False` en `detector`
- [x] 3.2 En la rama de evento fotométrico de `detect()`, resetear `_frame_count = 0` y establecer `_photometric_event = True`
- [x] 3.3 Al inicio de `detect()`, resetear `_photometric_event = False` antes de processar el frame
- [x] 3.4 Exponer función pública `last_photometric_event() -> bool` que retorna `_photometric_event`

## 4. Módulo orchestrator — descarte de múltiples detecciones y snapshot fotométrico

- [x] 4.1 Tras `detector.detect(frame)`, verificar `detector.last_photometric_event()`; si `True`, llamar `storage.save(frame, prefix="fondo_cambiado")` y continuar al siguiente frame
- [x] 4.2 Si `len(detections) > 1`, llamar `storage.save(frame, prefix="desechada_double")` y continuar sin publicar MQTT
- [x] 4.3 Verificar que `storage.save()` acepta un parámetro `prefix` opcional o que los nuevos prefijos son compatibles con la firma actual; actualizar si es necesario

## 5. Actualizar debug.py

- [x] 5.1 Eliminar referencias a `min_aspect_ratio` / `max_aspect_ratio` del filtro de contornos en `debug.py`
- [x] 5.2 Añadir filtro físico en el bucle de contornos de `debug.py` (mismo criterio que detector)
- [x] 5.3 Añadir anotación de dimensiones físicas en cm en el texto de cada bounding box (ej. `2.3cm × 1.8cm`)
- [x] 5.4 Implementar el bloque de frame con múltiples detecciones: anotar en naranja, imprimir `[!] DESECHADA DOUBLE (N objetos)`, guardar con prefijo `desechada_double_`
- [x] 5.5 Actualizar el bloque de evento fotométrico: imprimir `[!] CAMBIO FOTOMÉTRICO — reiniciando warmup (diff: X.X)`, guardar con prefijo `fondo_cambiado_`
- [x] 5.6 Actualizar el guardado de frames normales (1 detección) para usar prefijo `debug_` explícitamente

## 6. Verificación

- [x] 6.1 Verificar con frame sintético que un blob cuadrado con área válida y dimensiones dentro de máximos es detectado (aspect ratio ya no lo rechaza)
- [x] 6.2 Verificar con frame sintético que un blob grande (excede ambas dimensiones físicas) es rechazado
- [x] 6.3 Verificar que `last_photometric_event()` devuelve `True` al inyectar un cambio de luminancia y `False` en el siguiente frame
- [ ] 6.4 Ejecutar `python3 debug.py` con la cámara real y confirmar que se ven los tres tipos de guardado (`debug_`, `desechada_double_`, `fondo_cambiado_`)
- [ ] 6.5 Ajustar `pixels_per_cm` midiendo un objeto de tamaño conocido frente a la cámara y verificar que las dimensiones anotadas en `debug.py` son correctas
