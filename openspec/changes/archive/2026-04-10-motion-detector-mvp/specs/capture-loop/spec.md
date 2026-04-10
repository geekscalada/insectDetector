## REMOVED Requirements

### Requirement: orchestrator.run ejecuta un bucle de captura limitado
**Reason**: El bucle limitado por `capture_limit` servía únicamente para validar la infraestructura de captura y almacenamiento. El sistema de producción requiere ejecución continua hasta señal de parada.
**Migration**: Eliminar `orchestrator.capture_limit` de `config.yaml`. El proceso se detiene con Ctrl+C o SIGTERM.

## ADDED Requirements

### Requirement: orchestrator.run ejecuta un bucle continuo de detección hasta señal de parada
El módulo `orchestrator` SHALL exponer `run(config: dict) -> None` que captura frames de forma indefinida usando `FrameSource`, llama a `detector.detect(frame)` en cada frame, y guarda el frame con `storage.save` únicamente cuando `detect()` devuelve al menos una detección Y ha transcurrido más de `cooldown_seconds` desde el último guardado. El bucle SHALL terminar limpiamente al recibir `KeyboardInterrupt` o `SIGTERM`.

El orchestrator SHALL inicializar el detector pasando `config['detector']` en la inicialización del módulo.

#### Scenario: El orchestrator no guarda frames sin detecciones
- **WHEN** `detector.detect()` devuelve `[]` para todos los frames durante N segundos
- **THEN** no se crea ningún fichero JPEG en `storage.output_dir`

#### Scenario: El orchestrator guarda cuando hay detección y cooldown expirado
- **WHEN** `detector.detect()` devuelve al menos una `Detection` Y han transcurrido más de `cooldown_seconds` desde el último guardado
- **THEN** se crea exactamente un fichero JPEG mediante `storage.save`

#### Scenario: El cooldown suprime guardados repetidos durante un evento
- **WHEN** `detector.detect()` devuelve detecciones en frames consecutivos dentro de la ventana de `cooldown_seconds`
- **THEN** solo se guarda el primer frame positivo — los frames positivos dentro del cooldown no generan fichero

#### Scenario: Un error de storage se registra pero el bucle continúa
- **WHEN** `storage.save` lanza excepción
- **THEN** el orchestrator registra el error con `print` y continúa el bucle sin terminar el proceso

#### Scenario: El bucle termina limpiamente con Ctrl+C
- **WHEN** el proceso recibe `KeyboardInterrupt` mientras el bucle está activo
- **THEN** el orchestrator termina sin error no controlado — puede registrar un mensaje de parada con `print`
