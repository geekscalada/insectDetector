## ADDED Requirements

### Requirement: config.yaml centraliza todos los parámetros del sistema
El sistema SHALL tener un fichero `config.yaml` en la raíz del proyecto que sea la única fuente de verdad para todos los parámetros configurables. Ningún valor numérico, ruta, dirección IP ni parámetro de algoritmo SHALL aparecer hardcodeado en el código fuente.

#### Scenario: config.yaml contiene la sección camera
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene la clave `camera.fps` con valor entero

#### Scenario: config.yaml contiene la sección detector con parámetros MOG2 y filtros
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.mog2_history`, `detector.mog2_var_threshold`, `detector.detect_shadows`, `detector.mog2_shadow_threshold`, `detector.morph_kernel_size`, `detector.morph_iterations`, `detector.morph_operator`, `detector.min_area`, `detector.max_area`, `detector.min_aspect_ratio`, `detector.max_aspect_ratio`, `detector.warmup_frames`

#### Scenario: config.yaml contiene los parámetros del filtro fotométrico bajo detector.photometric
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.photometric.enable` (bool), `detector.photometric.max_mean_diff` (float) y `detector.photometric.learning_rate` (float)

#### Scenario: config.yaml contiene la sección storage
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `storage.output_dir` con valor de ruta string

#### Scenario: config.yaml contiene la sección mqtt
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `mqtt.broker_host`, `mqtt.broker_port`, `mqtt.topic`, `mqtt.cooldown_seconds`

#### Scenario: config.yaml contiene la sección orchestrator sin capture_limit
- **WHEN** se lee `config.yaml`
- **THEN** el documento NO contiene `orchestrator.capture_limit`

---

### Requirement: main.py es el único punto de entrada del sistema
El sistema SHALL tener un `main.py` en la raíz que sea el único script ejecutable. SHALL cargar `config.yaml` con PyYAML, pasar la config al orchestrator y llamar a `orchestrator.run()`. SHALL tener menos de 30 líneas de código.

#### Scenario: main.py carga la configuración desde config.yaml
- **WHEN** se ejecuta `python main.py`
- **THEN** el sistema carga `config.yaml` desde el directorio de trabajo actual usando PyYAML sin hardcodear la ruta en el código más allá de la constante `"config.yaml"`

#### Scenario: main.py no contiene lógica de negocio
- **WHEN** se revisa el código de `main.py`
- **THEN** el fichero no contiene lógica de captura, detección, almacenamiento ni publicación MQTT — sólo carga config y delega al orchestrator

---

### Requirement: config.yaml puede contener parámetros opcionales de exposición fija de cámara
El fichero `config.yaml` PUEDE contener las claves opcionales `camera.exposure_time` (int, microsegundos), `camera.analogue_gain` (float) y `camera.awb_enable` (bool). Si están presentes, el módulo `capture` SHALL aplicarlas. Si están ausentes, el módulo `capture` usará el modo automático de libcamera.

#### Scenario: config.yaml puede omitir las claves de exposición fija sin error
- **WHEN** `config.yaml` no contiene `camera.exposure_time`, `camera.analogue_gain` ni `camera.awb_enable`
- **THEN** el sistema arranca correctamente y la cámara opera en modo automático

#### Scenario: config.yaml con claves de exposición fija son leídas por capture
- **WHEN** `config.yaml` contiene `camera.exposure_time`, `camera.analogue_gain` y `camera.awb_enable`
- **THEN** el módulo `capture` lee esos valores desde `config['camera']` y los aplica a picamera2 en la inicialización
