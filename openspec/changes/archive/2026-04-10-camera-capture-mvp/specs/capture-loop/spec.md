## ADDED Requirements

### Requirement: orchestrator.run ejecuta un bucle de captura limitado
El módulo `orchestrator` SHALL exponer `run(config: dict) -> None` que lee `config['camera']['fps']`, `config['storage']['output_dir']` y `config['orchestrator']['capture_limit']`, captura exactamente `capture_limit` frames usando `FrameSource`, guarda cada frame con `storage.save`, y termina limpiamente.

#### Scenario: Se guardan exactamente N ficheros tras la ejecución
- **WHEN** se ejecuta `run(config)` con `capture_limit = 5`
- **THEN** hay exactamente 5 ficheros JPEG en `storage.output_dir` con nombres de timestamp distintos

#### Scenario: El sistema termina solo sin intervención del usuario
- **WHEN** se ejecuta `run(config)` con `capture_limit = 5`
- **THEN** el proceso termina solo tras guardar los 5 frames — no requiere Ctrl+C ni señal externa

#### Scenario: Un error de storage se registra pero el bucle continúa
- **WHEN** `storage.save` lanza excepción en uno de los frames
- **THEN** el orchestrator registra el error con `print` y continúa capturando los frames restantes
