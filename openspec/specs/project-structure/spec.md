## ADDED Requirements

### Requirement: El proyecto tiene estructura de paquetes Python para los cinco módulos
El proyecto SHALL tener los directorios `src/capture/`, `src/detector/`, `src/storage/`, `src/publisher/`, `src/orchestrator/` cada uno con un fichero `__init__.py`. Estos ficheros SHALL existir vacíos para que los módulos sean importables antes de implementar su lógica.

#### Scenario: Todos los módulos son importables tras el scaffold
- **WHEN** se ejecuta `python -c "from src import capture, detector, storage, publisher, orchestrator"` desde la raíz del proyecto
- **THEN** no se produce ningún ImportError

---

### Requirement: requirements.txt declara las cuatro dependencias del stack
El proyecto SHALL tener un `requirements.txt` en la raíz que liste como mínimo: `opencv-python-headless`, `picamera2`, `paho-mqtt`, `pyyaml`. SHALL usar versiones mínimas (`>=`) no clavadas para compatibilidad con el entorno de la Raspberry Pi.

#### Scenario: requirements.txt contiene las cuatro dependencias
- **WHEN** se lee `requirements.txt`
- **THEN** el fichero contiene entradas para `opencv-python-headless`, `picamera2`, `paho-mqtt` y `pyyaml`

---

### Requirement: El directorio detections/ existe y está en .gitignore
El proyecto SHALL tener un directorio `detections/` con un `.gitkeep` para que git lo rastree vacío. El contenido de `detections/` (ficheros JPEG) SHALL estar excluido del control de versiones mediante `.gitignore`.

#### Scenario: detections/ existe pero sus JPEGs no se rastrean por git
- **WHEN** se genera un JPEG en `detections/` durante la ejecución
- **THEN** `git status` no muestra ese fichero como untracked ni staged
