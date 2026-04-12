## Context

El sistema actual implementa detección de movimiento con MOG2, un filtro morfológico configurable, y un filtro basado en área y aspect ratio. La pipeline de debug en `debug.py` replica manualmente el pipeline de producción con anotaciones visuales.

Los problemas observados:
1. El filtro de aspect ratio rechaza formas válidas de insectos (redondos, cuadrados).
2. El área mínima/máxima está en píxeles sin relación con el tamaño físico real.
3. Un cambio fotométrico suprime el frame pero no reinicia el aprendizaje del fondo.
4. Múltiples detecciones simultáneas no se tratan como posibles falsos positivos.
5. `debug.py` no muestra las dimensiones físicas ni categoriza los tipos de guardado.

La restricción de diseño más importante: los módulos mantienen sus responsabilidades estrictas. `detector` solo detecta, `storage` solo guarda, `orchestrator` coordina.

## Goals / Non-Goals

**Goals:**
- Detectar insectos de hasta 5 cm en cualquier dimensión física, independientemente de la forma.
- Reiniciar el aprendizaje del fondo cuando se detecta un cambio fotométrico global.
- Descartar frames con más de un objeto detectado (posibles artefactos ambientales), guardando evidencia.
- Guardar snapshot con prefijo `fondo_cambiado_` cuando hay cambio fotométrico.
- Actualizar `debug.py` para mostrar dimensiones físicas y categorizar los guardados.
- Facilitar la calibración iterativa mediante `pixels_per_cm` configurable.

**Non-Goals:**
- No se cambia el protocolo MQTT ni la estructura de alertas.
- No se refactoriza la arquitectura de módulos.
- No se añade threading ni procesamiento asíncrono.
- No se cambia el mecanismo de captura (`capture`).

## Decisions

### D1: Calibración por `pixels_per_cm` en lugar de geometría de cámara

Se añade un parámetro escalar `pixels_per_cm` en `config.yaml`. El usuario lo calibra midiendo un objeto de tamaño conocido. Los filtros de tamaño máximo en cm se convierten a píxeles multiplicando por este factor.

**Alternativa descartada**: usar parámetros intrínsecos de cámara (distancia focal + distancia de trabajo). Más preciso pero requiere calibración compleja y no es necesario para insectos a distancia fija.

### D2: Señal de evento fotométrico mediante estado de módulo público

`detector` expone una función `last_photometric_event() -> bool` que indica si la última llamada a `detect()` produjo un evento fotométrico. El `orchestrator` la consulta tras cada `detect()` para decidir si guardar el snapshot `fondo_cambiado_`.

**Alternativa descartada**: extender el tipo de retorno de `detect()` a tupla o dataclass. Rompe el contrato existente y requiere actualizar todos los consumidores (incluyendo `debug.py`).

### D3: El re-warmup se implementa reseteando `_frame_count`

Cuando el filtro fotométrico se activa, además de pasar `learningRate=0`, se resetea `_frame_count = 0`. Esto suprime detecciones durante los siguientes `warmup_frames` mientras MOG2 aprende las nuevas condiciones gradualmente.

**Alternativa descartada**: reinicializar el objeto MOG2 completamente. Más agresivo pero descarta todo el fondo aprendido; el reinicio gradual es suficiente y más estable.

### D4: Descarte de múltiples detecciones en el `orchestrator`

El `orchestrator` recibe todas las detecciones de `detect()`. Si `len(detections) > 1`, las descarta y llama a `storage.save()` con un prefijo especial. Esta es lógica de coordinación, no de detección.

**Alternativa descartada**: filtrar en `detect()`. El detector no tiene responsabilidad sobre cómo se tratan las detecciones múltiples a nivel de negocio.

### D5: Eliminar `min_aspect_ratio` / `max_aspect_ratio` del filtro de detección

Se eliminan los parámetros de aspect ratio de `config.yaml` y del código de `detector`. El único filtro geométrico activo pasa a ser: área mínima en píxeles (ruido) + dimensiones físicas máximas en cm.

**Alternativa**: mantener aspect ratio opcional con `enable: false`. Añade complejidad sin necesidad real — se puede reintroducir si surge un caso de uso.

## Risks / Trade-offs

- **[Riesgo] `pixels_per_cm` desajustado da filtros incorrectos** → Mitigation: `debug.py` muestra las dimensiones físicas de cada contorno para facilitar la verificación visual durante la calibración.
- **[Riesgo] Re-warmup pierde un insecto real que coincide con un cambio de luz** → Aceptado: un cambio de luz global hace la detección poco fiable de todos modos. Se guarda el snapshot para revisión manual.
- **[Riesgo] Descarte de múltiples detecciones puede perder insectos en grupo** → Aceptado como criterio de diseño explícito; la foto `desechada_double_` permite análisis posterior.
- **[Trade-off] Estado fotométrico expuesto como función pública** → Introduce acoplamiento ligero entre `orchestrator` y `detector`, pero es la opción más simple sin romper contratos de retorno.

## Migration Plan

1. Actualizar `config.yaml`: añadir `pixels_per_cm`, `max_width_cm`, `max_height_cm`; deprecar `min_aspect_ratio` y `max_aspect_ratio`.
2. Actualizar `src/detector/__init__.py`: quitar aspect ratio, añadir filtro físico, añadir re-warmup, añadir `last_photometric_event()`.
3. Actualizar `src/orchestrator/__init__.py`: añadir lógica de descarte múltiple y snapshot fotométrico.
4. Actualizar `debug.py`: reflejar nuevos estados y guardar fotos categorizadas.
5. Verificar los cambios con frames sintéticos (unit) y con la cámara real (integración iterativa).

## Open Questions

- **OQ1**: ¿Cuántos píxeles son 1 cm a la distancia de trabajo real? El usuario debe medir y configurar `pixels_per_cm` en la primera iteración.
- **OQ2**: ¿El `max_area` en píxeles sigue siendo necesario tras añadir `max_width_cm` / `max_height_cm`? Candidato a eliminar en una iteración posterior si el filtro físico lo hace redundante.
