## 1. Configuración — nuevas claves en config.yaml

- [x] 1.1 Añadir subsección `detector.photometric` en `config.yaml` con claves `enable` (bool), `max_mean_diff` (float) y `learning_rate` (float negativo = auto OpenCV)
- [x] 1.2 Añadir claves opcionales de cámara en `config.yaml`: `camera.exposure_time`, `camera.analogue_gain`, `camera.awb_enable` — comentadas por defecto (modo auto)
- [x] 1.3 Documentar con comentarios inline en `config.yaml` el significado y rango recomendado de cada nuevo parámetro

## 2. Módulo detector — filtro de estabilidad fotométrica

- [x] 2.1 Añadir atributo de estado `_prev_gray` (inicializado a `None`) en el inicializador del módulo `detector`
- [x] 2.2 Añadir atributo `_photometric_cfg` con la subsección `config['detector']['photometric']` en el inicializador
- [x] 2.3 Al inicio de `detect()`, convertir el frame actual a gris con `cv2.cvtColor`
- [x] 2.4 Si `_prev_gray` es `None` (primer frame): asignar el gris actual a `_prev_gray` y continuar el pipeline sin aplicar el filtro
- [x] 2.5 Si `photometric.enable` es `True`: calcular `mean_diff = np.mean(np.abs(curr_gray.astype(float) − _prev_gray.astype(float)))`
- [x] 2.6 Si `mean_diff > photometric.max_mean_diff`: actualizar `_prev_gray`, pasar `learningRate=0` a `MOG2.apply()` y devolver `[]`
- [x] 2.7 Si el frame es estable: pasar `learningRate=photometric.learning_rate` a `MOG2.apply()` en lugar de usar el valor por defecto
- [x] 2.8 Actualizar `_prev_gray` al gris del frame actual al final de cada llamada (tanto frames estables como inestables)

## 3. Módulo capture — exposición fija opcional

- [x] 3.1 En la inicialización de `FrameSource`, leer `config['camera'].get('exposure_time')`, `config['camera'].get('analogue_gain')` y `config['camera'].get('awb_enable')`
- [x] 3.2 Si `exposure_time` está presente: aplicar el controls dict a picamera2 con `{'ExposureTime': exposure_time}`
- [x] 3.3 Si `analogue_gain` está presente: aplicar `{'AnalogueGain': analogue_gain}` a picamera2
- [x] 3.4 Si `awb_enable` es `False`: aplicar `{'AwbEnable': False}` a picamera2
- [x] 3.5 Verificar que si ninguna de las tres claves está presente el comportamiento de `FrameSource` no cambia

## 4. Verificación

- [x] 4.1 Probar el filtro fotométrico con frames sintéticos: un frame uniforme seguido de uno con diferencia media > umbral → `detect()` devuelve `[]`
- [x] 4.2 Probar el primer frame: `detect()` no suprime aunque no haya `prev_gray`
- [x] 4.3 Probar con `photometric.enable: False`: el filtro no actúa y MOG2 sigue operando normalmente
- [x] 4.4 Verificar que `learningRate=0` se pasa en frames inestables inspeccionando el estado del modelo de fondo (background no cambia con frame inestable)
- [ ] 4.5 Verificar manualmente en Raspberry Pi que los parches falsos del fondo desaparecen al activar el filtro con un umbral calibrado
