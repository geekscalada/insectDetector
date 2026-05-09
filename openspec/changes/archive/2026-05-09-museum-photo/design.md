## Context

El sistema guarda JPEGs de evidencia solo cuando el detector dispara. Esto crea huecos visuales en el histórico: no hay forma de saber qué aspecto tenía la escena entre detecciones, ni de diagnosticar a posteriori por qué el modelo falló (falso positivo, falso negativo) o cómo cambió la iluminación a lo largo del día.

La cámara ya genera frames a 10 FPS para el detector. Aprovechar uno de esos frames cada N segundos para construir un archivo fotográfico de la escena tiene coste casi nulo.

## Goals / Non-Goals

**Goals:**
- Guardar un frame de "referencia de museo" a intervalo fijo, independientemente de si hay detecciones.
- Organizar los frames por carpeta de día para facilitar la navegación manual.
- Purgar automáticamente al arrancar las carpetas con más antigüedad que `retention_days`.
- Añadir la sección `museum` a `config.yaml` como única fuente de verdad para los parámetros.

**Non-Goals:**
- Segunda instancia de cámara o captura adicional — se reutiliza el frame ya disponible en cada iteración.
- Anotación visual del frame de museo (sin bounding boxes, solo el frame raw).
- Compresión diferencial ni deduplicación de frames similares.
- Rotación de logs MQTT ni integración de museo con el canal de alertas.

## Decisions

### Decisión 1: `museum_storage` vive en `src/storage/museum.py`

**Alternativa considerada:** Añadir funciones directamente en `src/storage/__init__.py`.

**Razón de la elección:** Museo y evidencias son responsabilidades distintas (layout de directorios diferente, semántica de error diferente, lógica de purga específica de museo). Colocarlas en el mismo archivo mezclaría dos comportamientos sin beneficio. `museum.py` como submódulo sigue el patrón de separación del proyecto y es fácil de aislar en tests.

### Decisión 2: Firma con parámetros concretos — el orchestrator extrae de config

**Alternativa considerada:** `museum_storage.save(frame, timestamp, config)` pasando el dict completo.

**Razón de la elección:** Pasar `config` acopla el módulo de storage al esquema de `config.yaml`. Si se renombra una clave, hay que cambiar el módulo de storage. Con parámetros concretos, el módulo solo sabe guardar archivos; el orchestrator, que ya carga config, extrae los valores antes de llamar. Es el mismo patrón que usa `storage.save()` hoy.

**Firmas resultantes:**
```python
# src/storage/museum.py
def save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path: ...
def purge(output_dir: str, retention_days: int) -> None: ...
```

### Decisión 3: Layout de directorios `output_dir/YYYY-MM-DD/YYYY-MM-DD_HH-mm-ss.jpg`

Carpetas por día para facilitar la navegación y la purga. El nombre del fichero incluye la fecha completa para que sea legible fuera del contexto del directorio padre.

### Decisión 4: `museum_storage.save()` no propaga excepciones

Perder un frame de museo es aceptable — hay otro dentro de `interval_seconds`. El orchestrator captura la excepción, la registra con `print` y continúa el bucle. Mismo tratamiento que `publisher.publish()`.

**Contraste con `storage.save()`:** este sí propaga porque perder evidencias de detección silenciosamente no es aceptable.

### Decisión 5: El primer frame se guarda al arrancar

`last_museum_ts = None` en la inicialización del orchestrator dispara inmediatamente en la primera iteración del bucle. Esto proporciona una referencia visual del estado inicial de la escena.

### Decisión 6: La purga se ejecuta una sola vez al arrancar

`museum_storage.purge()` se llama en el orchestrator justo antes de entrar al bucle. No se purga en caliente ni de forma periódica — una purga al arrancar es suficiente para el MVP.

## Risks / Trade-offs

- **Disco lleno si `retention_days` es alto y el intervalo bajo.** A 5 s/frame con JPEGs de ~200 KB → ~3,4 GB/día. Con 3 días de retención → ~10 GB. Documentar esto en `config.yaml` con estimación orientativa.
- **Purga basada en nombre de directorio, no en mtime.** Si un directorio se crea con nombre incorrecto no se purgará. Riesgo mínimo porque `museum.py` es el único que crea esos directorios.
- **Primer frame puede ser inestable fotométricamente** (MOG2 aún calentando). El frame se guarda igual — es un frame de referencia, no de detección, así que la inestabilidad no perjudica nada.
