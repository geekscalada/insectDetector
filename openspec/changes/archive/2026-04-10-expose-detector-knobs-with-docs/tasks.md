## 1. Nuevos parámetros en config.yaml

- [x] 1.1 Añadir `detector.mog2_shadow_threshold: 0.5` a `config.yaml`
- [x] 1.2 Añadir `detector.morph_operator: "open"` a `config.yaml`

## 2. Documentación inline en config.yaml

- [x] 2.1 Añadir comentarios a la sección `camera:` (`fps`)
- [x] 2.2 Añadir comentarios a todos los parámetros de la sección `detector:` (incluyendo los dos nuevos)
- [x] 2.3 Añadir comentarios a la sección `storage:` (`output_dir`)
- [x] 2.4 Añadir comentarios a la sección `mqtt:` (`broker_host`, `broker_port`, `topic`, `cooldown_seconds`)

## 3. Módulo detector

- [x] 3.1 Leer `mog2_shadow_threshold` desde config y pasarlo a `cv2.createBackgroundSubtractorMOG2()` en la inicialización del módulo
- [x] 3.2 Leer `morph_operator` desde config, mapearlo a la constante OpenCV (`MORPH_OPEN`, `MORPH_CLOSE`, `MORPH_ERODE`, `MORPH_DILATE`) y aplicarlo en el pipeline morfológico en lugar de la operación hardcodeada actual

## 4. Verificación

- [x] 4.1 Ejecutar los tests existentes del detector para confirmar que el comportamiento por defecto (`open`, `shadow_threshold: 0.5`) es idéntico al anterior
- [x] 4.2 Verificar manualmente que un config con `morph_operator: "close"` no lanza excepción al arrancar
