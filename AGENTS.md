# AGENTS.md — insectDetector

## Objetivo

Sistema headless de detección de insectos ejecutado en Raspberry Pi: captura vídeo cenital con Camera Module 2 NoIR, detecta movimiento por sustracción de fondo MOG2, guarda evidencias JPEG y publica alertas MQTT a Home Assistant.

La arquitectura es un **monolito modular Python** con separación estricta de responsabilidades entre cinco módulos (`capture`, `detector`, `storage`, `publisher`, `orchestrator`) y un único fichero de configuración (`config.yaml`).

---

## Paradigmas de desarrollo

### Simplicidad sobre completitud

Este es un sistema MVP personal. La prioridad es que funcione de forma fiable y sea fácil de entender, no que sea exhaustivo o elegante.

- No añadir abstracciones, clases base ni patrones de diseño que no sean necesarios ahora.
- No introducir threading, asyncio ni procesamiento paralelo sin una necesidad demostrada y documentada.
- No añadir manejo de errores para escenarios que no pueden ocurrir en la práctica.
- Si hay dos soluciones y una es más simple, elegir la simple aunque sea menos "correcta".

### Separación de responsabilidades como regla dura

Cada módulo tiene una única responsabilidad. Esta separación no es una recomendación, es una restricción del diseño:

- `capture` entrega frames, nada más.
- `detector` transforma frames en detecciones, nada más.
- `storage` y `publisher` son adaptadores de salida independientes entre sí.
- `orchestrator` cablea los módulos; no implementa lógica de negocio propia.

Cruzar estos límites requiere una decisión de diseño explícita, no una conveniencia de implementación.

### Configuración centralizada

`config.yaml` es la única fuente de verdad para parámetros. Ningún valor numérico, ruta, dirección IP ni parámetro de algoritmo puede aparecer hardcodeado en el código. El `orchestrator` carga la configuración una vez al inicio y la pasa a cada módulo en la inicialización.

### Contratos explícitos e inmutables

Los módulos se comunican a través de firmas de función estables. Cambiar una firma es un cambio de contrato: requiere actualizar todos los lados (productor y consumidor) en el mismo commit, y documentarlo aquí y en `investigacion-design.md`.

### Comportamiento de fallos definido por diseño

- `publisher.publish()` **nunca lanza excepción** — la pérdida de alertas MQTT es aceptable.
- `storage.save()` **sí propaga excepciones** — perder evidencias silenciosamente no es aceptable.
- El `orchestrator` captura los errores de `storage`, los registra con `print` y continúa el bucle.

Este comportamiento diferenciado es una decisión de diseño, no un descuido.

---

## Reglas globales

- Lee los ficheros del módulo afectado y `config.yaml` antes de proponer cualquier cambio.
- Los cambios deben ser pequeños y enfocados. No refactorices lo que no está roto.
- Si una tarea afecta a más de un módulo, identifica los contratos implicados antes de escribir código.
- Todo cambio en `config.yaml` debe reflejarse en `investigacion-design.md` si altera una decisión de diseño.
- Señala siempre riesgos, supuestos y verificaciones pendientes al terminar.

---

## Política de cambios en contratos

Ningún cambio de firma de función, tipo de retorno o semántica de error se hace sin:

1. Identificar todos los módulos que producen o consumen ese contrato.
2. Actualizar productor y consumidor en el mismo cambio.
3. Documentar el cambio en este fichero bajo la sección de contratos del skill `insectdetector-context`.

Los cambios breaking en contratos requieren revisión explícita antes de implementar.

---

## Política de pruebas mínimas

- Todo módulo nuevo o modificado debe verificarse con al menos un caso representativo antes de declararlo terminado.
- `capture` y `detector`: usar frames sintéticos (numpy arrays) — no se requiere hardware real.
- `storage`: verificar que el fichero se crea en la ruta correcta y que los errores de escritura se propagan.
- `publisher`: verificar que un fallo de conexión no lanza excepción al llamador.
- No se añade código de producción sin haber ejecutado al menos una verificación manual del área afectada.

---

## Política de cambios multi-módulo

Cuando una tarea afecte a más de un módulo:

1. Identifica todos los módulos y contratos implicados **antes** de escribir código.
2. Empieza por el contrato (firma, tipo de retorno) antes de implementar la lógica.
3. Propaga el cambio en orden: contrato → módulo productor → módulo consumidor → `orchestrator` si aplica.
4. No mezcles cambios funcionales con cambios de configuración en el mismo paso.

---

## Delegación recomendada

| Tarea / Área | Delegar a |
|--------------|-----------|
| Decisiones de arquitectura, diseño, trade-offs | `Investigator Architect` |
| Módulos `src/capture/` y `src/detector/` | `python-cv-implementer` |
| Módulos `src/storage/` y `src/publisher/` | `python-iot-implementer` |
| `src/orchestrator/`, `main.py`, `config.yaml` | `python-orchestrator-implementer` |
| Tareas multi-módulo o que cambian contratos | `app-orchestrator` |

---

## Formato de respuesta esperado

Cuando termines una tarea:

1. **Qué se ha cambiado** — lista concisa de ficheros y lógica modificada.
2. **Impacto por módulo** — indica qué módulos se ven afectados.
3. **Contratos modificados** — si alguna firma ha cambiado, indícalo explícitamente.
4. **Riesgos y supuestos** — qué puede fallar, qué se ha asumido.
5. **Pruebas** — qué verificaciones se han ejecutado o cuáles están pendientes.
