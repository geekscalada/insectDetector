# insectDetector — Documentación funcional

Sistema headless de detección de insectos para Raspberry Pi con Camera Module 2 NoIR. Captura vídeo cenital, detecta movimiento por sustracción de fondo, guarda evidencias fotográficas y publica alertas MQTT a Home Assistant.

---

## Índice

1. [Cómo lanzar la aplicación](#1-cómo-lanzar-la-aplicación)
2. [Arquitectura general](#2-arquitectura-general)
3. [Flujo principal de ejecución](#3-flujo-principal-de-ejecución)
4. [Módulos](#4-módulos)
   - [capture](#41-capture)
   - [detector](#42-detector)
   - [storage](#43-storage)
   - [publisher](#44-publisher-no-implementado)
   - [orchestrator](#45-orchestrator)
5. [Archivos fotográficos — `photo_historic/`](#5-archivos-fotográficos--photo_historic)
6. [Configuración — `config.yaml`](#6-configuración--configyaml)
7. [Herramienta de debug — `debug.py`](#7-herramienta-de-debug--debugpy-desactualizado)

---

## 1. Cómo lanzar la aplicación

### Requisitos previos

- Raspberry Pi (4 o 5) con Raspberry Pi OS Bookworm
- Camera Module 2 NoIR habilitada (`raspi-config` → Interface Options → Camera)
- Python 3.11+
- Broker MQTT accesible en red (p. ej. Mosquitto en Home Assistant)

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

Las dependencias son:

| Paquete | Uso |
|---|---|
| `opencv-python-headless>=4.8` | MOG2, morfología, anotación de frames |
| `picamera2>=0.3` | Captura desde Camera Module 2 NoIR |
| `paho-mqtt>=1.6` | Publicación de alertas al broker MQTT |
| `pyyaml>=6.0` | Lectura de `config.yaml` |

### Configuración previa al arranque

Editar `config.yaml` en la raíz del proyecto. Como mínimo, ajustar:

```yaml
mqtt:
  broker_host: "192.168.1.100"   # IP de tu broker MQTT / Home Assistant
```

El resto de parámetros tiene valores razonables por defecto. Consultar la sección [Configuración](#6-configuración--configyaml) para el detalle de cada uno.

### Arranque del sistema

```bash
python3 main.py
```

Para detener el sistema, pulsar `Ctrl+C`. El proceso termina limpiamente y libera la cámara.

### Arranque en modo debug (desarrollo / calibración)

El sistema de producción ya guarda imágenes categorizadas en `photo_historic/` para cada tipo de evento (`_detection`, `_desechada_double`, `_fondo_cambiado`). Esto es suficiente para inspeccionar el comportamiento del detector sin herramientas adicionales.

Existe un script `debug.py` en la raíz, pero está desactualizado: replica internamente el pipeline de detección con lógica propia (no llama a `detector.detect()`), usa el formato de nombre de fichero anterior y no refleja el estado actual del sistema. **No se recomienda usarlo.**

---

## 2. Arquitectura general

El sistema es un **monolito modular Python** con cinco módulos de responsabilidad única:

```
main.py  ──────────────────────────────────────────────────────────
             │ carga config.yaml
             ▼
         orchestrator  ──────── FrameSource (capture)
             │                       │ frames BGR @ 10 FPS
             │  ◄─────────────────── │
             │
             ├──► detector.detect(frame)
             │         │
             │         ▼
             │    list[Detection]
             │
             ├──► storage.save(frame, prefix)    ──► photo_historic/
             │
             ├──► museum_storage.save(frame)     ──► photo_historic/
             │
             └──► publisher.publish(payload)     ──► broker MQTT  ⚠ no implementado
```

### Separación de responsabilidades

| Módulo | Responsabilidad única | Nunca hace |
|---|---|---|
| `capture` | Entrega frames BGR desde picamera2 | CV, I/O de ficheros, red |
| `detector` | MOG2 + morfología + filtros → `list[Detection]` | I/O de cualquier tipo |
| `storage` | Escribe JPEGs de evidencia en disco | CV, MQTT |
| `publisher` | Publicará alertas MQTT (fire-and-forget) — **no implementado aún** | CV, ficheros |
| `orchestrator` | Cablea módulos, gestiona cooldown y archivo periódico | CV directo, I/O directo |

---

## 3. Flujo principal de ejecución

### Arranque (una sola vez)

1. `main.py` carga `config.yaml` con PyYAML.
2. `orchestrator.run(config)` es llamado.
3. El orchestrator llama a `museum_storage.purge(output_dir, retention_days)` — elimina subdirectorios de `photo_historic/` con más de `retention_days` días de antigüedad.
4. Se inicializa `detector` con los parámetros de `config['detector']`.

### Bucle de detección (por cada frame)

```
┌─ FrameSource → frame BGR
│
├─ 1. ¿Evento fotométrico?
│     detector.detect(frame)
│     └─ Si mean_diff > max_mean_diff:
│           → Guardar frame con prefijo "fondo_cambiado"
│           → Reiniciar warmup de MOG2
│           → Continuar al siguiente frame (skip detección)
│
├─ 2. ¿Fase de warmup?
│     Si _frame_count < warmup_frames:
│           → No se emiten detecciones (MOG2 aprendiendo el fondo)
│
├─ 3. ¿Cuántos contornos qualifying?
│     detector.last_qualifying_count() > 1:
│           → Guardar frame con prefijo "desechada_double"
│           → NO publicar MQTT
│     == 0:
│           → No guardar nada, no publicar
│
├─ 4. ¿Detección válida + cooldown expirado?
│     detect() devuelve ≥ 1 Detection
│     AND tiempo desde last_saved_at > cooldown_seconds:
│           → annotate(frame, detections)
│           → storage.save(annotated_frame, prefix="detection")
│           → publisher.publish(payload)
│
└─ 5. ¿Intervalo de museo cumplido?
      (now - last_museum_ts) >= interval_seconds:
            → museum_storage.save(frame)   [frame sin anotar]
            → Actualizar last_museum_ts
```

### Comportamiento ante errores

| Componente | Si falla | Consecuencia |
|---|---|---|
| `storage.save` | Propaga excepción | El orchestrator la captura con `print` y **continúa** el bucle |
| `museum_storage.save` | Propaga excepción | El orchestrator la captura con `print`, **no actualiza** `last_museum_ts`, y continúa |
| `publisher.publish` | **Nunca lanza** excepción | La pérdida de alertas MQTT es aceptable (QoS 0) |

---

## 4. Módulos

### 4.1 `capture`

**Contrato:**

```python
FrameSource(config: dict)  # generador → yields np.ndarray (H, W, 3) uint8 BGR
```

`FrameSource` es un generador que inicializa picamera2, configura la captura a `config['camera']['fps']` FPS y entrega frames BGR indefinidamente. Al romper el bucle, libera el hardware de cámara.

**Parámetros de cámara opcionales** (si están presentes en `config.yaml`, se aplican fijos; si están ausentes, la cámara usa modo automático):

| Clave | Tipo | Efecto |
|---|---|---|
| `camera.exposure_time` | int (µs) | Fija el tiempo de exposición; desactiva AEC/AGC |
| `camera.analogue_gain` | float | Fija la ganancia analógica |
| `camera.awb_enable` | bool | `false` desactiva el balance de blancos automático |

---

### 4.2 `detector`

**Contratos:**

```python
init(config: dict) -> None
detect(frame: np.ndarray) -> list[Detection]
annotate(frame: np.ndarray, detections: list[Detection]) -> np.ndarray
last_photometric_event() -> bool
last_qualifying_count() -> int
```

El módulo mantiene estado interno entre llamadas (MOG2, frame anterior para comparación fotométrica, contador de frames de warmup).

#### Pipeline de `detect(frame)`

```
frame BGR
   │
   ├─ Calcular mean(abs(gray_actual − gray_anterior))
   │     Si > photometric.max_mean_diff  →  evento fotométrico:
   │         devolver [], MOG2.apply(learningRate=0), resetear warmup
   │
   ├─ MOG2.apply(frame)  →  máscara de foreground (255 = fg, 127 = sombra)
   │
   ├─ Morfología configurable (open / close / erode / dilate)
   │     kernel: morph_kernel_size × morph_kernel_size
   │     iteraciones: morph_iterations
   │
   ├─ findContours en la máscara
   │
   └─ Por cada contorno:
         área < min_area  →  descartar
         w > max_width_px AND h > max_height_px  →  descartar (tamaño físico)
         si pasa todos los filtros  →  añadir a list[Detection]
```

#### Warmup

Durante las primeras `warmup_frames` llamadas, `detect()` devuelve siempre `[]` para que MOG2 aprenda el fondo inicial sin emitir falsas alarmas. Un evento fotométrico reinicia este contador a cero.

#### Filtro fotométrico

Compara la luminancia media entre el frame actual y el anterior. Un cambio brusco global (p. ej. encendido de luz, reajuste de autoexposición) activa el filtro: `detect()` devuelve `[]`, MOG2 no aprende ese frame, y se resetea el warmup.

#### Filtro de tamaño físico

Los parámetros `pixels_per_cm`, `max_width_cm` y `max_height_cm` se convierten a píxeles en la inicialización. Un contorno se **rechaza** solo si supera el máximo en **ambas** dimensiones — si cumple al menos una, pasa el filtro.

#### `Detection`

```python
Detection(
    bbox: tuple[int, int, int, int],  # (x, y, w, h)
    area: float,
    aspect_ratio: float
)
```

---

### 4.3 `storage`

**Contrato:**

```python
save(frame: np.ndarray, timestamp: datetime, output_dir: str, prefix: str = "detection") -> Path
# Lanza excepción si falla la escritura — nunca la silencia
```

Escribe el frame como JPEG en:

```
{output_dir}/YYYY-MM-DD/YYYY-MM-DD-HH-MM-SS_{prefix}.jpg
```

Crea el subdirectorio de día si no existe. El prefijo determina el tipo de imagen (ver sección [5](#5-archivos-fotográficos--photo_historic)).

---

### 4.4 `publisher`

**Contrato:**

```python
publish(payload: dict) -> None
# Nunca lanza excepción — pérdida aceptada (QoS 0)
```

> **Estado actual:** el módulo `src/publisher/__init__.py` existe pero está **vacío — MQTT no está implementado**. El orchestrator tampoco llama a `publisher.publish()`. La sección `mqtt` de `config.yaml` solo se usa para leer `cooldown_seconds`, que controla el intervalo mínimo entre guardados de evidencia.

Cuando se implemente, publicará el payload como JSON en el topic MQTT configurado. La semántica diseñada es fire-and-forget (QoS 0): si la conexión falla, la alerta se pierde silenciosamente sin afectar al bucle de detección.

---

### 4.5 `orchestrator`

**Contrato:**

```python
run(config: dict) -> None
```

Punto de entrada del bucle principal. Cablea todos los módulos, gestiona:

- **Cooldown de detección:** mínimo `mqtt.cooldown_seconds` entre dos guardados de evidencia consecutivos.
- **Archivo periódico de museo:** frame de referencia cada `museum.interval_seconds` segundos.
- **Purga al arranque:** elimina directorios de `photo_historic/` más antiguos de `museum.retention_days` días.
- **Captura de errores de storage:** registra con `print` y continúa el bucle.

---

## 5. Archivos fotográficos — `photo_historic/`

Todas las imágenes — tanto frames periódicos de referencia como evidencias de detección — se guardan en un único directorio `photo_historic/`, organizado por subdirectorios de día:

```
photo_historic/
└── YYYY-MM-DD/
    ├── YYYY-MM-DD-HH-MM-SS_museum.jpg          # frame periódico de referencia
    ├── YYYY-MM-DD-HH-MM-SS_detection.jpg       # detección válida (frame anotado)
    ├── YYYY-MM-DD-HH-MM-SS_desechada_double.jpg  # descartado por múltiples blobs
    └── YYYY-MM-DD-HH-MM-SS_fondo_cambiado.jpg  # descartado por evento fotométrico
```

### Tipos de imagen

| Sufijo | Quién lo genera | Cuándo |
|---|---|---|
| `_museum` | `museum_storage.save` | Cada `museum.interval_seconds` segundos |
| `_detection` | `storage.save` (default) | Detección válida + cooldown expirado |
| `_desechada_double` | `storage.save` | Más de un contorno qualifying en el frame |
| `_fondo_cambiado` | `storage.save` | Cambio fotométrico global detectado |

### Política de retención

Al arrancar, el orchestrator llama a `museum_storage.purge(output_dir, retention_days)`, que elimina recursivamente todos los subdirectorios de `photo_historic/` cuya fecha sea anterior a `hoy - retention_days`. La purga afecta a **todos los tipos** de imagen del día (incluidas evidencias de detección) — la política de retención es global y unificada.

### Estimación de uso de disco

Con configuración por defecto (`interval_seconds: 5`, ~200 KB/JPEG):

- ~17 280 frames de museo/día → ~3,4 GB/día
- Con `retention_days: 3` → hasta ~10 GB máximo en disco

Ajustar `interval_seconds` o `retention_days` según el espacio disponible.

---

## 6. Configuración — `config.yaml`

Única fuente de verdad para todos los parámetros. Ningún valor numérico, ruta ni dirección IP aparece hardcodeado en el código.

### Secciones

#### `camera`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `fps` | int | Fotogramas por segundo (recomendado: 5–30) |
| `width`, `height` | int | Resolución de captura |
| `exposure_time` | int (µs) | *(Opcional)* Exposición fija; desactiva AEC/AGC |
| `analogue_gain` | float | *(Opcional)* Ganancia analógica fija (1.0–8.0) |
| `awb_enable` | bool | `false` desactiva el balance de blancos automático |

#### `detector`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `mog2_history` | int | Frames usados por MOG2 para aprender el fondo (100–2000) |
| `mog2_var_threshold` | float | Umbral de varianza MOG2 (8–256) |
| `detect_shadows` | bool | Activa detección de sombras en MOG2 |
| `mog2_shadow_threshold` | float | Umbral de intensidad para clasificar sombras (0.0–1.0) |
| `morph_kernel_size` | int | Tamaño del kernel morfológico (2–7) |
| `morph_iterations` | int | Iteraciones del filtro morfológico (1–3) |
| `morph_operator` | string | `open`, `close`, `erode` o `dilate` |
| `min_area` | float | Área mínima de blob en px² para considerarse detección |
| `max_area` | float | Área máxima de blob en px² |
| `pixels_per_cm` | float | Píxeles por cm a la distancia de trabajo (calibrar) |
| `max_width_cm` | float | Dimensión física máxima en ancho (cm) |
| `max_height_cm` | float | Dimensión física máxima en alto (cm) |
| `min_solidity` | float | Solidez mínima del blob (área / bounding box; 0.0–1.0) |
| `warmup_frames` | int | Frames iniciales sin detección para estabilizar MOG2 (20–100) |
| `photometric.enable` | bool | Activa el filtro de estabilidad fotométrica |
| `photometric.max_mean_diff` | float | Umbral de diferencia de luminancia inter-frame (3.0–15.0) |
| `photometric.learning_rate` | float | Learning rate de MOG2 en frames estables (-1 = automático) |

#### `mqtt`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `broker_host` | string | IP o hostname del broker MQTT |
| `broker_port` | int | Puerto TCP (1883 estándar, 8883 TLS) |
| `topic` | string | Topic MQTT al que se publican las alertas |
| `cooldown_seconds` | int | Tiempo mínimo entre dos alertas consecutivas |

#### `museum`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `interval_seconds` | int | Intervalo entre capturas periódicas de referencia (5–60 s) |
| `retention_days` | int | Días de retención de `photo_historic/` |

#### `photo_historic`

| Parámetro | Tipo | Descripción |
|---|---|---|
| `output_dir` | string | Directorio raíz para todas las imágenes guardadas |

---

## 7. Herramienta de debug — `debug.py` ⚠ desactualizado

`debug.py` existe en la raíz pero está **desactualizado y no se recomienda usar**. Duplica internamente la lógica de detección con un pipeline propio que no refleja el estado actual de `src/detector/`, usa el formato de nombre de fichero anterior y no integra los cambios recientes (p. ej. `photo_historic/`).

### Alternativa recomendada

El sistema de producción ya cubre las necesidades de inspección: cada frame relevante se guarda en `photo_historic/YYYY-MM-DD/` con el sufijo que identifica su causa. Basta con arrancar con `python3 main.py` y revisar los ficheros generados:

| Sufijo | Qué indica |
|---|---|
| `_detection` | Detección confirmada (frame anotado con bounding box) |
| `_desechada_double` | Frame con más de un blob qualifying — posible falso positivo |
| `_fondo_cambiado` | Cambio fotométrico global — MOG2 ha reiniciado el warmup |
| `_museum` | Frame periódico de referencia — contexto visual previo a eventos |
