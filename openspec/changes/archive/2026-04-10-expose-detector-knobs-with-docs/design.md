## Context

`config.yaml` expone 10 parámetros bajo `detector:`, pero el módulo `detector` tiene dos valores hardcodeados que afectan al comportamiento de detección:

- `shadowThreshold` de MOG2 (valor fijo 0.5 por defecto de OpenCV): controla a partir de qué intensidad un píxel se clasifica como sombra en lugar de foreground.
- El operador morfológico: actualmente siempre aplica erosión seguida de dilatación (equivalente a `OPEN`), sin posibilidad de cambiar la operación.

Adicionalmente, ningún parámetro de `config.yaml` tiene documentación inline, lo que obliga a consultar código o specs para entender el efecto de cada valor.

Las restricciones del proyecto son: configuración centralizada en `config.yaml`, sin valores hardcodeados en código, sin cambios de firma en módulos.

## Goals / Non-Goals

**Goals:**
- Exponer `mog2_shadow_threshold` y `morph_operator` como parámetros en `config.yaml`.
- El módulo `detector` lee y aplica ambos parámetros en lugar de sus defaults hardcodeados.
- Todos los parámetros de `config.yaml` tienen comentarios YAML inline en español que describen comportamiento, rango recomendado y efecto direccional (subir/bajar valor).

**Non-Goals:**
- No se expone la resolución de cámara en este cambio (pertenece al módulo `capture`).
- No se refactoriza el resto de `detector` más allá de los dos nuevos parámetros.
- No se añade validación de rangos en tiempo de carga (fuera de alcance del MVP).

## Decisions

### Documentación con comentarios YAML (`#`)

PyYAML serializa y deserializa el fichero como dict ignorando los comentarios. Se puede documentar cada parámetro con una o dos líneas de comentario YAML sin ningún cambio de código en los módulos que leen la config. Alternativa descartada: añadir una sección `docs:` en `config.yaml` — complicaría la estructura sin beneficio real.

### `morph_operator` como string `open | close | erode | dilate`

Los cuatro valores mapean directamente a constantes de OpenCV (`cv2.MORPH_OPEN`, `cv2.MORPH_CLOSE`, `cv2.MORPH_ERODE`, `cv2.MORPH_DILATE`). El detector convierte el string a constante con un dict de mapeo. Valor por defecto: `open` (erosión+dilatación, comportamiento actual). Alternativa descartada: exponer dos parámetros separados `morph_op_1` y `morph_op_2` — añade complejidad sin caso de uso demostrado.

### `mog2_shadow_threshold` como float [0.0, 1.0]

OpenCV usa 0.5 por defecto. Valores bajos (~0.2) clasifican menos píxeles como sombra (más foreground), valores altos (~0.9) clasifican más como sombra (menos foreground). Solo tiene efecto cuando `detect_shadows: true`.

## Risks / Trade-offs

- [Riesgo] El string de `morph_operator` podría escribirse mal en config → el detector fallará con `KeyError` al arrancar. Mitigación: aceptable en MVP; el error es inmediato y visible en los logs.
- [Trade-off] Los comentarios YAML se pierden si alguien reescribe el fichero con PyYAML (que no preserva comentarios). Mitigación: los comentarios viven en el fichero en el repositorio y se restauran con git.
