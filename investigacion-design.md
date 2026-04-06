# Investigación y Diseño: InsectDetector

**Fecha:** 2026-04-06

## Resumen ejecutivo

Sistema de detección de insectos (cucarachas) por diferencia de frames, ejecutado en Raspberry Pi con cámara cenital NoIR. Al detectar un positivo, guarda una fotografía de evidencia y emite una alerta MQTT hacia un servidor de red local.

## Propuesta analizada

App que capture vídeo desde una Raspberry Pi con Camera Module 2 NoIR apuntando al techo, detecte insectos de menos de 10cm (principalmente cucarachas) por diferencia de frames, filtre personas y animales por tamaño, guarde imágenes de los positivos y notifique por MQTT a un broker en red local que distribuye alertas vía Home Assistant.

---

## Decisiones tomadas

### Hardware

- **Decisión:** Raspberry Pi 4 (POC) → Raspberry Pi 5 (producción) + Camera Module 2 NoIR
- **Alternativas consideradas:** Cámara USB genérica, webcam
- **Razón:** Hardware ya disponible. El módulo NoIR permite detección nocturna con iluminación IR sin modificar el sistema.

### Stack

- **Decisión:** Python con OpenCV + picamera2
- **Alternativas consideradas:** Node.js + opencv4nodejs, Python puro sin OpenCV, Python backend + frontend TypeScript
- **Razón:** Python es el estándar de la industria para CV en Raspberry Pi. `picamera2` es la librería oficial para el Camera Module 2 en Pi OS moderno. OpenCV ofrece exactamente las primitivas necesarias (MOG2, morfología, contornos). Node.js + opencv4nodejs fue descartado por complejidad de compilación en ARM y escaso soporte para picamera2.

### Arquitectura general del sistema

- **Decisión:** Monolito modular en Python, headless, autónomo en la Pi
- **Alternativas consideradas:** Python backend + frontend web TS, Python puro con UI local (Tkinter)
- **Razón:** La Pi opera sin monitor. No se necesita UI remota — la monitorización se hace revisando las imágenes guardadas manualmente. Monolito modular cumple el principio de simplicidad y es extensible sin sobreingeniería.

```
[Raspberry Pi "detectora"]
  Camera NoIR → Frame diff → Filtro tamaño/forma
       ↓                          ↓
  Guarda JPEG               Publica MQTT (fire-and-forget)
  detections/               (cooldown 60s)
                                  ↓
                         [Broker MQTT - servidor red local]
                                  ↓
                         [Home Assistant] → alertas (fuera de scope)
```

### Algoritmo de detección

- **Decisión:** MOG2 (`cv2.createBackgroundSubtractorMOG2`, `detectShadows=True`) + filtrado morfológico (erosión → dilatación)
- **Alternativas consideradas:** Diferencia simple de 2 frames, diferencia de 3 frames (temporal), homografía para calibración de perspectiva
- **Razón:** MOG2 es robusto ante cambios graduales de luz y cámara fija. `detectShadows=True` descarta sombras de personas — el mayor fuente de falsos positivos en este escenario. La diferencia de 3 frames fue descartada porque fragmenta blobs de objetos rápidos (cucarachas).

### Filtrado de objetos detectados

- **Decisión:** Filtro bidireccional de área (P2: rango amplio `MIN=50px² → MAX=5000px²`) + filtro de aspect ratio (~1.5:1 a 3:1)
- **Alternativas consideradas:** P1 (zonas calibradas por región del frame), P3 (homografía/calibración métrica)
- **Razón:** P2 es suficiente para POC sin calibración manual. El aspect ratio es el discriminador clave: cucarachas son alargadas, personas vistas desde el techo son casi circulares. P1 queda como evolución si P2 produce demasiados falsos positivos.

### Captura de vídeo

- **Decisión:** 10 FPS
- **Alternativas consideradas:** 5fps (menor cobertura), 25fps (saturación CPU Pi 4)
- **Razón:** Punto óptimo entre cobertura de insectos rápidos y carga computacional de la Pi 4. El background MOG2 se estabiliza bien a esta frecuencia.

### Almacenamiento de evidencias (MVP)

- **Decisión:** Un fichero JPEG por detección — primer frame positivo
- **Alternativas consideradas:** Carpeta de frames individuales durante 60s, vídeo MP4 del evento, híbrido JPEG + MP4
- **Razón:** Máxima simplicidad para validar que la detección funciona. Extensible a clip de vídeo una vez validado el sistema.
- **Ruta:** `detections/YYYY-MM-DDTHH:MM:SS.jpg`

### Notificación MQTT

- **Decisión:** Fire-and-forget (QoS 0) con cooldown de 60 segundos entre alertas
- **Alternativas consideradas:** QoS 1 con reintentos automáticos
- **Razón:** Uso personal, pérdida ocasional de alertas es aceptable. El cooldown de 60s evita spam al broker durante un evento sostenido. Simplicidad sobre robustez en esta fase.

### Estructura del proyecto

```
insectDetector/
├── src/
│   ├── capture/          # Interfaz con picamera2 → frames
│   ├── detector/         # MOG2 + morfología + filtros de tamaño y forma
│   ├── storage/          # Guardar JPEG con timestamp
│   ├── publisher/        # Cliente MQTT fire-and-forget
│   └── orchestrator/     # Bucle principal, cooldown, coordinación
├── config.yaml           # Umbrales, FPS, topic MQTT, rutas, parámetros MOG2
├── main.py               # Punto de entrada
└── requirements.txt      # opencv-python, picamera2, paho-mqtt, pyyaml
```

**Patrón de comunicación interna:** el `orchestrator` invoca `detector` frame a frame; si hay positivo y el cooldown ha expirado, llama a `storage.save()` y `publisher.publish()` de forma independiente (no bloqueante entre sí).

---

## Riesgos identificados

- **Falsos positivos por sombras de personas:** Mitigación — `detectShadows=True` en MOG2 + filtro de aspect ratio.
- **Fragmentación de blobs en cucarachas rápidas:** Mitigación — MOG2 en lugar de diff de 3 frames; dilatación morfológica une fragmentos.
- **Perspectiva variable (misma cucaracha, distinto tamaño en píxeles):** Mitigación — rango P2 amplio en POC. Escalada a P1 (zonas calibradas) si es necesario.
- **Almacenamiento que crece sin límite:** Mitigación — no gestionado en MVP; añadir rotación de ficheros (ej: máximo 7 días o 1GB) en siguiente iteración.
- **Pérdida de alertas MQTT por red inestable:** Mitigación — aceptado conscientemente (fire-and-forget). Escalar a QoS 1 si resulta problemático.
- **Rendimiento en Pi 4 con MOG2 a 10fps:** Mitigación — Pi 4 tiene capacidad suficiente para resolución reducida (ej: 640×480); si hay saturación, bajar resolución antes de bajar FPS.

---

## Próximos pasos

1. Configurar entorno Python en Raspberry Pi 4 con `picamera2`, `opencv-python`, `paho-mqtt`
2. Implementar módulo `capture` — leer frames de Camera Module 2 NoIR a 10fps
3. Implementar módulo `detector` — MOG2 + morfología + filtros área y aspect ratio
4. Implementar módulo `storage` — guardar JPEG con timestamp en `detections/`
5. Implementar módulo `publisher` — cliente MQTT fire-and-forget
6. Implementar `orchestrator` — bucle principal con cooldown de 60s
7. Calibrar parámetros MOG2 y umbrales de filtro in-situ con cucarachas reales
8. Validar tasa de falsos positivos/negativos en condiciones reales (personas, animales, niños)
9. Migrar a Raspberry Pi 5 para producción
10. (Futuro) Añadir clip MP4 de 60s por evento y rotación de almacenamiento
