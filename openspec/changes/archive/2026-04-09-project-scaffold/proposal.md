## Why

El proyecto no tiene aún ningún fichero fuente. Antes de poder implementar cualquier módulo (capture, detector, storage, publisher, orchestrator), hace falta el esqueleto: la estructura de directorios, la configuración centralizada y el punto de entrada. Sin esto, ningún agente implementador puede comenzar a trabajar de forma aislada.

## What Changes

- Crear `config.yaml` con todos los parámetros del sistema (FPS, umbrales MOG2, filtros de área y aspect ratio, cooldown MQTT, topic, rutas)
- Crear `requirements.txt` con las cuatro dependencias del stack (opencv-python-headless, picamera2, paho-mqtt, pyyaml)
- Crear la estructura de directorios `src/capture/`, `src/detector/`, `src/storage/`, `src/publisher/`, `src/orchestrator/` con ficheros `__init__.py` vacíos
- Crear `main.py` (< 30 líneas) que carga config y delega al orchestrator
- Crear `detections/` con `.gitkeep` y entrada en `.gitignore`

## Capabilities

### New Capabilities

- `config-and-entrypoint`: Configuración centralizada en `config.yaml` y punto de entrada `main.py` que carga la config y arranca el sistema
- `project-structure`: Esqueleto de directorios `src/` con módulos vacíos listos para ser implementados

### Modified Capabilities

## Impact

- No hay código existente que se rompa; este cambio crea el suelo sobre el que se construirán todos los módulos
- Determina los nombres de parámetros en `config.yaml` que todos los módulos posteriores importarán
- `requirements.txt` fija las versiones mínimas del entorno de ejecución en la Raspberry Pi
