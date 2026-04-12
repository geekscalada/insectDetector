## MODIFIED Requirements

### Requirement: config.yaml contiene la sección detector con parámetros MOG2 y filtros
El sistema SHALL tener un fichero `config.yaml` en la raíz del proyecto que sea la única fuente de verdad para todos los parámetros configurables. La sección `detector` SHALL incluir los parámetros MOG2, morfológicos y de filtrado de contornos ya existentes, y además SHALL incluir una subsección `photometric` con los parámetros del filtro de estabilidad fotométrica.

#### Scenario: config.yaml contiene la sección detector con parámetros MOG2 y filtros
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.mog2_history`, `detector.mog2_var_threshold`, `detector.detect_shadows`, `detector.mog2_shadow_threshold`, `detector.morph_kernel_size`, `detector.morph_iterations`, `detector.morph_operator`, `detector.min_area`, `detector.max_area`, `detector.min_aspect_ratio`, `detector.max_aspect_ratio`, `detector.warmup_frames`

#### Scenario: config.yaml contiene los parámetros del filtro fotométrico bajo detector.photometric
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `detector.photometric.enable` (bool), `detector.photometric.max_mean_diff` (float) y `detector.photometric.learning_rate` (float)

## ADDED Requirements

### Requirement: config.yaml puede contener parámetros opcionales de exposición fija de cámara
El fichero `config.yaml` PUEDE contener las claves opcionales `camera.exposure_time` (int, microsegundos), `camera.analogue_gain` (float) y `camera.awb_enable` (bool). Si están presentes, el módulo `capture` SHALL aplicarlas. Si están ausentes, el módulo `capture` usará el modo automático de libcamera.

#### Scenario: config.yaml puede omitir las claves de exposición fija sin error
- **WHEN** `config.yaml` no contiene `camera.exposure_time`, `camera.analogue_gain` ni `camera.awb_enable`
- **THEN** el sistema arranca correctamente y la cámara opera en modo automático

#### Scenario: config.yaml con claves de exposición fija son leídas por capture
- **WHEN** `config.yaml` contiene `camera.exposure_time`, `camera.analogue_gain` y `camera.awb_enable`
- **THEN** el módulo `capture` lee esos valores desde `config['camera']` y los aplica a picamera2 en la inicialización
