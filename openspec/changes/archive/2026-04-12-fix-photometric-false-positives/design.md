## Context

El módulo `capture` no fija la exposición, ganancia ni balance de blancos de la cámara. Los algoritmos AEC/AGC y AWB de libcamera ajustan automáticamente los parámetros fotométricos en función de la escena, produciendo variaciones de luminancia globales o semiglobales entre frames consecutivos. MOG2 interpreta esas variaciones como foreground, generando falsos positivos en forma de múltiples parches pequeños dispersos por el fondo, aunque no haya ningún objeto real.

La arquitectura actual no tiene ningún mecanismo para distinguir entre un cambio fotométrico de la cámara y el movimiento de un insecto.

## Goals / Non-Goals

**Goals:**
- Eliminar falsos positivos causados por ajustes fotométricos automáticos de la cámara
- Proteger el modelo de fondo de MOG2 de ser contaminado en frames inestables
- Dar al operador control sobre la exposición de la cámara desde `config.yaml`

**Non-Goals:**
- Análisis de coherencia espacial o tracking de blobs entre frames
- Detección de condiciones de iluminación ambiental (día/noche)
- Persistencia o consolidación de detecciones a lo largo de varios frames

## Decisions

### Decisión 1: El filtro fotométrico vive dentro del módulo `detector`

**Alternativa considerada:** Implementarlo en el `orchestrator` como un guard pre-detect.

**Razón de la elección:** El análisis de estabilidad de frame es lógica de visión computacional sobre numpy arrays. Según los límites del proyecto, todo lo que es CV pertenece a `detector`. El `orchestrator` no debe contener lógica de negocio; solo cablea módulos. Colocarlo en `detector` evita que ningún contrato externo cambie.

### Decisión 2: La firma de `detect()` no cambia

**Alternativa considerada:** Añadir un valor de retorno adicional (p.ej. `tuple[list[Detection], bool]`) que indique si el frame era inestable.

**Razón de la elección:** Cambiar la firma rompería el contrato actual. El `orchestrator` solo necesita saber si hay detecciones; recibir `[]` cuando el frame es inestable es semánticamente correcto. El flag de estabilidad es un detalle de implementación interna.

### Decisión 3: `learningRate=0` cuando el frame es inestable

MOG2 acepta un parámetro `learningRate` en cada llamada a `apply()`. Cuando el frame es inestable se pasa `learningRate=0` para evitar que el modelo de fondo asuma los píxeles alterados como nuevo fondo. Cuando el frame es estable se usa el valor configurado (valor negativo = automático en OpenCV).

### Decisión 4: Métrica de inestabilidad — `mean(abs(curr_gray − prev_gray))`

**Alternativas consideradas:** Porcentaje de píxeles con diferencia > d, distancia entre histogramas de gris.

**Razón de la elección:** La media absoluta es simple, O(1) con numpy, y captura tanto cambios distribuidos débiles —autoexposición— como cambios locales fuertes. Es suficiente para el MVP. Si resulta insuficiente puede complementarse con el % de píxeles en una segunda iteración.

### Decisión 5: Exposición fija en `capture` es opcional y backward-compatible

Los parámetros `camera.exposure_time`, `camera.analogue_gain` y `camera.awb_enable` son opcionales en `config.yaml`. Si están ausentes la cámara sigue en modo automático. Esto permite habilitar la corrección gradualmente sin romper instalaciones existentes.

## Risks / Trade-offs

- **Umbral demasiado conservador** → supresión de detecciones durante cambios reales de luz natural (amanecer, paso de nube). Mitigación: documentar `photometric.max_mean_diff` con valores empíricos de referencia en `config.yaml`.
- **Primer frame sin `prev_gray`** → no se puede evaluar inestabilidad; el frame pasa siempre. Riesgo mínimo; es un caso singular.
- **`learningRate=0` durante muchos frames seguidos** → si el fondo cambia por razones legítimas (mover la cámara), el modelo no se actualiza. Mitigación: reiniciar el proceso actualiza el modelo desde cero vía `warmup_frames`.
- **Exposición fija en luz baja** → puede oscurecer el frame y reducir la detectabilidad de insectos. Mitigación: parámetro opcional; el operador decide activarlo y calibra el valor.
