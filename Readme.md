# insectDetector

Sistema headless de detección de insectos para Raspberry Pi con Camera Module 2 NoIR. Captura vídeo cenital, detecta movimiento por sustracción de fondo MOG2, guarda evidencias JPEG y publica alertas MQTT a Home Assistant.

---

## Arranque rápido

```bash
pip install -r requirements.txt
python3 main.py
```

Editar `config.yaml` antes de arrancar — como mínimo ajustar `mqtt.broker_host`.

---

## Arquitectura

Monolito modular Python con cinco módulos de responsabilidad única:

| Módulo | Responsabilidad |
|---|---|
| `capture` | Entrega frames BGR desde picamera2 a 10 FPS |
| `detector` | MOG2 + morfología + filtros → `list[Detection]` |
| `storage` | Escribe JPEGs de evidencia en `photo_historic/` |
| `publisher` | Publicará alertas MQTT (no implementado aún) |
| `orchestrator` | Cablea módulos, gestiona cooldown y archivo periódico |

---

## Imágenes generadas

Todas las imágenes se guardan en `photo_historic/YYYY-MM-DD/` con sufijo que identifica la causa:

| Sufijo | Cuándo |
|---|---|
| `_detection` | Detección válida con cooldown expirado |
| `_desechada_double` | Más de un blob qualifying (posible falso positivo) |
| `_fondo_cambiado` | Cambio fotométrico global — MOG2 reinicia warmup |
| `_museum` | Frame periódico de referencia cada `museum.interval_seconds` s |

---

## Configuración principal (`config.yaml`)

- **`camera`** — resolución, FPS, exposición y ganancia opcionales
- **`detector`** — parámetros MOG2, morfología, filtros de área y tamaño físico, warmup
- **`mqtt`** — broker, topic, `cooldown_seconds` entre alertas consecutivas
- **`museum`** — intervalo entre capturas de referencia y días de retención
- **`photo_historic.output_dir`** — directorio raíz de todas las imágenes

Consultar [DOCUMENTATION.md](DOCUMENTATION.md) para el detalle completo de cada parámetro.
