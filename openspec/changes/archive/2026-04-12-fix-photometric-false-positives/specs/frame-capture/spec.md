## ADDED Requirements

### Requirement: FrameSource aplica parámetros de exposición fija cuando están configurados
El módulo `capture` SHALL leer las claves opcionales `camera.exposure_time`, `camera.analogue_gain` y `camera.awb_enable` de la configuración recibida en la inicialización. Si `camera.exposure_time` está presente, SHALL fijar el tiempo de exposición de picamera2 al valor indicado (en microsegundos). Si `camera.analogue_gain` está presente, SHALL fijar la ganancia analógica. Si `camera.awb_enable` es `False`, SHALL desactivar el ajuste automático de balance de blancos. Si cualquiera de estas claves está ausente, el parámetro correspondiente SHALL usar el modo automático de libcamera sin modificación.

#### Scenario: Exposición fija se aplica cuando camera.exposure_time está configurado
- **WHEN** `config['camera']['exposure_time']` contiene un valor entero positivo (microsegundos)
- **THEN** picamera2 recibe ese valor como tiempo de exposición fijo antes de iniciar la captura

#### Scenario: Ganancia analógica fija se aplica cuando camera.analogue_gain está configurado
- **WHEN** `config['camera']['analogue_gain']` contiene un valor float positivo
- **THEN** picamera2 recibe ese valor como ganancia analógica fija antes de iniciar la captura

#### Scenario: AWB desactivado cuando camera.awb_enable es False
- **WHEN** `config['camera']['awb_enable']` es `False`
- **THEN** picamera2 desactiva el balance de blancos automático antes de iniciar la captura

#### Scenario: Parámetros ausentes mantienen modo automático
- **WHEN** `config['camera']` no contiene `exposure_time`, `analogue_gain` ni `awb_enable`
- **THEN** picamera2 se inicializa con los valores automáticos por defecto — el comportamiento preexistente no cambia
