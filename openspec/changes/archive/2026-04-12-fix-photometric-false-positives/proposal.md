## Why

MOG2 interpreta los ajustes automáticos de exposición, ganancia y balance de blancos de la cámara como cambio real en la escena, generando falsos positivos en forma de pequeños parches dispersos en el fondo aunque no haya ningún insecto. La causa raíz es doble: (1) la cámara varía fotométricamente el frame sin movimiento real, y (2) el detector no distingue un cambio de luminancia global de un evento de insecto.

## What Changes

- Se añade un **filtro de estabilidad fotométrica inter-frame** en el módulo `detector`: antes de ejecutar MOG2, se compara la luminancia media del frame actual con la del anterior; si el cambio supera un umbral configurable, la detección se suprime y el aprendizaje de MOG2 se congela (`learningRate=0`).
- Se añaden parámetros de **exposición fija** en el módulo `capture`: tiempo de exposición, ganancia analógica y desactivación de AWB se configuran en `config.yaml` y se aplican a la cámara en la inicialización, eliminando la fuente de variación fotométrica en origen.
- Se añaden las claves de configuración correspondientes en `config.yaml` con valores por defecto seguros y documentados.

Ningún cambio en las firmas de los módulos públicos (`detect`, `FrameSource`, `save`, `publish`).

## Capabilities

### New Capabilities

- `photometric-stability-filter`: Lógica interna del módulo `detector` que mantiene el frame gris anterior como estado, calcula `mean(abs(curr_gray − prev_gray))` por frame, y cuando supera el umbral: devuelve `[]` desde `detect()` y pasa `learningRate=0` a `MOG2.apply()` para no contaminar el modelo de fondo.

### Modified Capabilities

- `motion-detection`: El comportamiento de `detect()` se amplía para incluir el check de estabilidad fotométrica antes de aplicar MOG2. La firma no cambia, pero se añaden nuevos parámetros de configuración obligatorios bajo `detector.photometric`.
- `frame-capture`: El módulo `capture` debe aceptar y aplicar parámetros de exposición fija desde `config['camera']` (`exposure_time`, `analogue_gain`, `awb_enable`). Cuando no se configuran, el comportamiento actual (auto) se mantiene.
- `config-and-entrypoint`: Se añaden claves nuevas bajo `detector.photometric` y opcionalmente bajo `camera` para exposición fija.

## Impact

- **`src/detector/`**: estado interno adicional (`prev_gray`), parámetros nuevos, lógica pre-MOG2.
- **`src/capture/`**: inicialización de cámara con exposición fija si se configura.
- **`config.yaml`**: nuevas claves bajo `detector.photometric` y `camera`.
- **Sin cambios en**: `storage`, `publisher`, `orchestrator`, `main.py`, contratos públicos.
