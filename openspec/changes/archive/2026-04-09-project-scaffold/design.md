## Context

El proyecto insectDetector no tiene código fuente todavía. Partimos del documento `investigacion-design.md` que recoge todas las decisiones de arquitectura y parámetros ya tomados. Este scaffold crea el suelo sobre el que todos los módulos implementadores trabajarán en paralelo. La Raspberry Pi correrá Python 3.11+ en Pi OS Bookworm.

## Goals / Non-Goals

**Goals:**
- Crear `config.yaml` con todos los parámetros del sistema nombrados conforme al diseño
- Crear `requirements.txt` con las cuatro dependencias y versiones mínimas probadas
- Crear la estructura de directorios `src/<module>/__init__.py` para los cinco módulos
- Crear `main.py` como punto de entrada delgado (< 30 líneas)
- Crear `detections/` con `.gitkeep` y registrarlo en `.gitignore`

**Non-Goals:**
- Implementar lógica en ningún módulo (los `__init__.py` quedan vacíos)
- Configurar entorno de Raspberry Pi o instalar dependencias
- Crear tests en este cambio

## Decisions

### Nombres de claves en `config.yaml`

Todos los módulos importarán estos nombres. Cambiarlos después es un cambio de contrato. Se establece ahora la nomenclatura definitiva:

```yaml
camera:
  fps: 10                        # capture

detector:
  mog2_history: 500
  mog2_var_threshold: 16
  detect_shadows: true
  morph_kernel_size: 3           # erosion & dilation
  morph_iterations: 1
  min_area: 50                   # px²
  max_area: 5000                 # px²
  min_aspect_ratio: 1.5
  max_aspect_ratio: 3.0

storage:
  output_dir: detections/

mqtt:
  broker_host: "192.168.1.100"
  broker_port: 1883
  topic: "insectdetector/alert"
  cooldown_seconds: 60
```

**Alternativa descartada:** configuración plana sin secciones — descartada porque los módulos acceden sólo a su propia sección, y la jerarquía evita colisiones de nombres.

### Estructura de paquetes Python

Cada módulo es un paquete Python (`src/<module>/__init__.py`) para permitir imports relativos limpios (`from src.capture import ...`). No se usa `src` como paquete instalable (`setup.py`/`pyproject.toml`) porque es un script headless, no una librería.

### `main.py` como orquestador de arranque

`main.py` sólo hace tres cosas: cargar `config.yaml` con PyYAML, instanciar el orchestrator con la config, y llamar a `orchestrator.run()`. No contiene lógica de negocio.

## Risks / Trade-offs

- [Los nombres de parámetros quedan fijados] → Mitigation: se definen ahora de forma deliberada y se documentan en este fichero; cualquier cambio posterior requiere actualizar todos los módulos consumidores.
- [Versiones de dependencias en `requirements.txt`] → Mitigation: se establecen versiones mínimas (`>=`) no clavadas, para que funcionen en la Pi sin conflictos; se puede clavear en producción.
- [`src` no es paquete instalable] → Aceptado: es un script de sistema, no una librería. Si en el futuro se necesita instalar, se añade `pyproject.toml`.
