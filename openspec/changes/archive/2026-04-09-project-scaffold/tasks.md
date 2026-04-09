## 1. Configuración centralizada

- [x] 1.1 Crear `config.yaml` en la raíz con las secciones `camera`, `detector`, `storage` y `mqtt` y todos sus parámetros tal como define `design.md`
- [x] 1.2 Verificar que el YAML es válido (`python -c "import yaml; yaml.safe_load(open('config.yaml'))"`)

## 2. Dependencias

- [x] 2.1 Crear `requirements.txt` con `opencv-python-headless>=4.8`, `picamera2>=0.3`, `paho-mqtt>=1.6`, `pyyaml>=6.0`

## 3. Estructura de paquetes

- [x] 3.1 Crear `src/__init__.py` (vacío)
- [x] 3.2 Crear `src/capture/__init__.py` (vacío)
- [x] 3.3 Crear `src/detector/__init__.py` (vacío)
- [x] 3.4 Crear `src/storage/__init__.py` (vacío)
- [x] 3.5 Crear `src/publisher/__init__.py` (vacío)
- [x] 3.6 Crear `src/orchestrator/__init__.py` (vacío)
- [x] 3.7 Verificar que todos los módulos son importables (`python -c "from src import capture, detector, storage, publisher, orchestrator"`)

## 4. Punto de entrada

- [x] 4.1 Crear `main.py` que carga `config.yaml` con PyYAML y delega a `orchestrator.run(config)` — menos de 30 líneas, sin lógica de negocio

## 5. Directorio de evidencias

- [x] 5.1 Crear `detections/.gitkeep`
- [x] 5.2 Crear o actualizar `.gitignore` para excluir `detections/*.jpg` (mantener el `.gitkeep`)
