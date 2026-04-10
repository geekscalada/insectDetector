## Why

`config.yaml` no expone todos los parámetros que controlan el comportamiento real del detector: el umbral de sombras de MOG2 (`shadowThreshold`) y el tipo de operador morfológico están fijos en el código sin posibilidad de ajuste. Además, ningún parámetro tiene documentación inline, lo que obliga a leer el código fuente o los specs para entender qué efecto tiene cada valor. Esto dificulta el tuning en campo desde la Raspberry Pi.

## What Changes

- Se añaden a `config.yaml` los parámetros `detector.mog2_shadow_threshold` y `detector.morph_operator` que actualmente están hardcodeados en el módulo `detector`.
- Se añaden comentarios YAML inline en español a cada parámetro de `config.yaml`, describiendo: qué controla, rango de valores recomendado, y el efecto de subir o bajar el valor.
- El módulo `detector` lee y aplica los dos nuevos parámetros en lugar de sus valores hardcodeados.

## Capabilities

### New Capabilities

- `config-inline-docs`: `config.yaml` incluye comentarios inline en español que documentan el comportamiento, rango y efecto direccional de cada parámetro del sistema.

### Modified Capabilities

- `config-and-entrypoint`: se añaden `detector.mog2_shadow_threshold` y `detector.morph_operator` como parámetros obligatorios en `config.yaml`, ampliando los escenarios del spec existente.
- `motion-detection`: `detector.detect()` SHALL leer `mog2_shadow_threshold` y `morph_operator` desde config en lugar de usar valores hardcodeados.

## Impact

- `config.yaml`: se añaden 2 claves y se añaden comentarios a todas las claves existentes.
- `src/detector/__init__.py`: se refactorizan las llamadas a `cv2.createBackgroundSubtractorMOG2()` y al pipeline morfológico para usar los nuevos parámetros de config.
- Sin cambios en firmas de función ni en otros módulos.
