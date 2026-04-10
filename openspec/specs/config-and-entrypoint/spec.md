## ADDED Requirements

### Requirement: config.yaml centraliza todos los parámetros del sistema
El sistema SHALL tener un fichero `config.yaml` en la raíz del proyecto que sea la única fuente de verdad para todos los parámetros configurables. Ningún valor numérico, ruta, dirección IP ni parámetro de algoritmo SHALL aparecer hardcodeado en el código fuente.

#### Scenario: config.yaml contiene la sección camera
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene la clave `camera.fps` con valor entero

#### Scenario: config.yaml contiene la sección detector con parámetros MOG2 y filtros
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.mog2_history`, `detector.mog2_var_threshold`, `detector.detect_shadows`, `detector.morph_kernel_size`, `detector.morph_iterations`, `detector.min_area`, `detector.max_area`, `detector.min_aspect_ratio`, `detector.max_aspect_ratio`

#### Scenario: config.yaml contiene la sección storage
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `storage.output_dir` con valor de ruta string

#### Scenario: config.yaml contiene la sección mqtt
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `mqtt.broker_host`, `mqtt.broker_port`, `mqtt.topic`, `mqtt.cooldown_seconds`

#### Scenario: config.yaml contiene la sección orchestrator con capture_limit
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `orchestrator.capture_limit` con valor entero positivo

---

### Requirement: main.py es el único punto de entrada del sistema
El sistema SHALL tener un `main.py` en la raíz que sea el único script ejecutable. SHALL cargar `config.yaml` con PyYAML, pasar la config al orchestrator y llamar a `orchestrator.run()`. SHALL tener menos de 30 líneas de código.

#### Scenario: main.py carga la configuración desde config.yaml
- **WHEN** se ejecuta `python main.py`
- **THEN** el sistema carga `config.yaml` desde el directorio de trabajo actual usando PyYAML sin hardcodear la ruta en el código más allá de la constante `"config.yaml"`

#### Scenario: main.py no contiene lógica de negocio
- **WHEN** se revisa el código de `main.py`
- **THEN** el fichero no contiene lógica de captura, detección, almacenamiento ni publicación MQTT — sólo carga config y delega al orchestrator
