## Requirements

### Requirement: debug.py replica el pipeline de producción con anotaciones visuales y log de filtrado
El script `debug.py` SHALL ejecutar el mismo pipeline de detección que el sistema de producción (captura → desenfoque → MOG2 → morfología → contornos → filtros), pero en lugar de guardar evidencias ni publicar MQTT, SHALL anotar cada contorno relevante directamente sobre el frame con su estado y motivo de descarte, incluyendo las dimensiones físicas en cm calculadas con `pixels_per_cm`. SHALL categorizar los frames guardados con los prefijos correctos según el estado del frame: `YYYYMMDD_HHmmss_mmm_debug.jpg`, `YYYYMMDD_HHmmss_mmm_desechada_double.jpg`, `YYYYMMDD_HHmmss_mmm_fondo_cambiado.jpg`.

Este script es una herramienta de desarrollo, no código de producción. SHALL poder ejecutarse de forma independiente con `python3 debug.py` y SHALL terminar limpiamente con `Ctrl+C`.

#### Scenario: Contorno que pasa todos los filtros se muestra en verde
- **WHEN** un contorno supera `min_area` y sus dimensiones físicas están dentro de los máximos configurados
- **THEN** se dibuja un rectángulo verde sobre el frame anotado con el texto `INSECTO (!), Wcm x Hcm` mostrando las dimensiones físicas y se imprime `[✓] INSECTO DETECTADO` con área, aspect ratio y dimensiones en cm por consola

#### Scenario: Contorno descartado por filtros se muestra en rojo con el motivo
- **WHEN** un contorno supera el umbral mínimo de visibilidad (`min_area / 3`) pero no pasa alguno de los filtros de producción
- **THEN** se dibuja un rectángulo rojo con el motivo de descarte (ej. `A=450 px` o `W=6.2cm>5.0cm`) y se imprime `[x] Objeto ignorado` por consola

#### Scenario: Contornos por debajo del umbral mínimo de visibilidad se silencian
- **WHEN** un contorno tiene área menor que `min_area / 3`
- **THEN** no se genera anotación visual ni mensaje de consola

#### Scenario: Frame con cambio fotométrico se notifica, resetea warmup y guarda snapshot
- **WHEN** el filtro fotométrico detecta `mean_diff > photometric.max_mean_diff`
- **THEN** se imprime `[!] CAMBIO FOTOMÉTRICO — reiniciando warmup (diff: X.X)` y se guarda un JPEG con prefijo `fondo_cambiado`

#### Scenario: Frame con múltiples contornos qualifying se descarta y guarda como desechada_double
- **WHEN** después de aplicar `min_area` hay más de un contorno qualifying en el frame (sean verdes o rojos)
- **THEN** se imprime `[!] DESECHADA DOUBLE (N objetos qualifying)`, se guardan los bounding boxes con sus colores originales, y se guarda un JPEG con sufijo `desechada_double`

#### Scenario: Frame con exactamente una detección válida se guarda como debug normal
- **WHEN** hay exactamente un contorno válido en el frame
- **THEN** se guarda un JPEG con sufijo `debug` con throttle de 1 segundo

#### Scenario: Warmup inicial suprime detecciones y muestra progreso
- **WHEN** el número de frames procesados no supera `warmup_frames`
- **THEN** no se realizan anotaciones ni se guardan imágenes; cada 10 frames se imprime el progreso de calibración por consola

#### Scenario: debug.py termina limpiamente con Ctrl+C
- **WHEN** el usuario interrumpe con `KeyboardInterrupt`
- **THEN** el script termina sin traza de error y libera la cámara correctamente
