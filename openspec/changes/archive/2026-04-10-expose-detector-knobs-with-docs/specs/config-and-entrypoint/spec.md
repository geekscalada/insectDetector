## MODIFIED Requirements

### Requirement: config.yaml centraliza todos los parámetros del sistema
El sistema SHALL tener un fichero `config.yaml` en la raíz del proyecto que sea la única fuente de verdad para todos los parámetros configurables. Ningún valor numérico, ruta, dirección IP ni parámetro de algoritmo SHALL aparecer hardcodeado en el código fuente.

#### Scenario: config.yaml contiene la sección camera
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene la clave `camera.fps` con valor entero

#### Scenario: config.yaml contiene la sección detector con parámetros MOG2 y filtros
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.mog2_history`, `detector.mog2_var_threshold`, `detector.detect_shadows`, `detector.mog2_shadow_threshold`, `detector.morph_kernel_size`, `detector.morph_iterations`, `detector.morph_operator`, `detector.min_area`, `detector.max_area`, `detector.min_aspect_ratio`, `detector.max_aspect_ratio`, `detector.warmup_frames`

#### Scenario: config.yaml contiene la sección storage
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `storage.output_dir` con valor de ruta string

#### Scenario: config.yaml contiene la sección mqtt
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `mqtt.broker_host`, `mqtt.broker_port`, `mqtt.topic`, `mqtt.cooldown_seconds`

#### Scenario: config.yaml contiene la sección orchestrator sin capture_limit
- **WHEN** se lee `config.yaml`
- **THEN** el documento NO contiene `orchestrator.capture_limit`
