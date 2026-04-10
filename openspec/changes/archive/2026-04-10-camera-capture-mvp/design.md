## Context

El scaffold del proyecto existe (`config.yaml`, `requirements.txt`, `main.py`, paquetes vacíos). Esta es la primera implementación ejecutable: tres módulos (`capture`, `storage`, `orchestrator`) se implementan con la mínima lógica necesaria para que el usuario pueda ejecutar `python main.py` en la Raspberry Pi y observar que se guardan 5 JPEGs en `detections/`. No hay detección, no hay MQTT.

La Pi corre Pi OS Bookworm con Camera Module 2 NoIR. `picamera2` es la librería oficial y ya está instalada en el sistema. OpenCV se instala desde `requirements.txt`.

## Goals / Non-Goals

**Goals:**
- Implementar `FrameSource` en `capture` usando picamera2, entregando frames BGR uint8 numpy a 10 FPS
- Implementar `storage.save(frame, timestamp)` que escribe JPEG con nombre timestamp en `detections/`
- Implementar `orchestrator.run(config)` con bucle limitado: captura `capture_limit` frames, guarda cada uno, termina
- Añadir `orchestrator.capture_limit` en `config.yaml`

**Non-Goals:**
- Detección de insectos (MOG2, filtros) — cambio futuro
- Publicación MQTT — cambio futuro
- Cooldown de alertas — no aplica en este MVP
- Manejo de reconexión de cámara o errores de hardware

## Decisions

### `FrameSource` como generador Python

`capture` expone un generador (`yield frame`) en lugar de una clase con método `read()`. Razón: el `orchestrator` consume frames en un `for frame in source` natural; no necesita gestionar ciclo de vida con `open()`/`close()`. picamera2 se inicializa en el constructor y se libera al finalizar el generador con `camera.stop()` en el bloque `finally`.

**Alternativa descartada:** clase `Camera` con `__enter__`/`__exit__` — añade complejidad de context manager sin beneficio en este uso.

### Firma de `FrameSource`

```python
# src/capture/__init__.py
def FrameSource(fps: int) -> Generator[np.ndarray, None, None]:
    ...
```

El `orchestrator` llama `FrameSource(config['camera']['fps'])`. No se pasa el objeto `config` entero a `capture` — sólo el parámetro que necesita, para mantener el acoplamiento mínimo.

### Bucle limitado en orchestrator (MVP)

`orchestrator.run(config)` itera sobre `FrameSource` con `enumerate` y rompe cuando `i >= capture_limit`. No hay lógica de detección ni cooldown todavía — sólo captura y guarda.

```python
for i, frame in enumerate(FrameSource(fps)):
    if i >= capture_limit:
        break
    storage.save(frame, datetime.now())
```

### Nombre de fichero JPEG

`storage.save` usa `datetime.isoformat()` con los `:` reemplazados por `-` para compatibilidad con sistemas de ficheros: `YYYY-MM-DDTHH-MM-SS.ffffff.jpg`. Se incluyen microsegundos para garantizar unicidad cuando se capturan múltiples frames por segundo (e.g. a 10 FPS). El directorio de salida viene de `config['storage']['output_dir']`.

**Alternativa descartada:** timestamp Unix — menos legible al revisar evidencias manualmente.

**Decisión de verificación:** el formato sin microsegundos (`HH-MM-SS`) causaba sobreescritura de ficheros a 10 FPS durante la verificación en Pi — los 5 frames se capturaban en <1 segundo y compartían nombre.

### Conversión BGR → JPEG

`cv2.imencode('.jpg', frame)` — OpenCV ya está como dependencia. No se usa `PIL`/`Pillow` para no añadir dependencia extra.

## Risks / Trade-offs

- [picamera2 no disponible en entorno de desarrollo] → No es riesgo: el módulo sólo se ejecuta en la Pi. Los `__init__.py` de `capture` son importables vacíos en dev, la implementación vive en un fichero separado.
- [BGR vs RGB] → picamera2 con `format="BGR888"` entrega BGR directamente compatible con OpenCV. Sin conversión.
- [`capture_limit` en config.yaml] → Es un parámetro de MVP, no de producción. Se puede eliminar en el change del pipeline completo sin romper contratos.
- [Fallo de `storage.save` si `detections/` no existe] → `storage.save` crea el directorio si no existe (`os.makedirs(..., exist_ok=True)`). El `.gitkeep` ya garantiza que existe en repo, pero la creación defensiva es segura.
