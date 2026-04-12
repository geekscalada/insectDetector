## ADDED Requirements

### Requirement: photometric-warmup-reset reinicia el fondo al detectar inestabilidad fotométrica
Cuando el filtro fotométrico detecta un cambio global (`mean_diff > photometric.max_mean_diff`), el módulo `detector` SHALL, además de devolver `[]` y aplicar MOG2 con `learningRate=0`, resetear `_frame_count = 0` para forzar re-warmup completo. SHALL también establecer el flag interno `_photometric_event = True` para que el `orchestrator` pueda consultarlo mediante la función pública `last_photometric_event() -> bool`. El flag SHALL resetearse a `False` al inicio de cada llamada a `detect()` y establecerse a `True` únicamente cuando ocurra el evento fotométrico.

El `orchestrator` SHALL, después de cada llamada a `detect()`, consultar `detector.last_photometric_event()`. Si es `True`, SHALL guardar el frame actual como snapshot usando `storage.save(frame, prefix="fondo_cambiado")`.

#### Scenario: Inestabilidad fotométrica resetea el contador de warmup
- **WHEN** `detect(frame)` detecta `mean_diff > photometric.max_mean_diff`
- **THEN** `_frame_count` se resetea a `0` para que las siguientes `warmup_frames` frames supriman detecciones mientras MOG2 aprende el nuevo fondo

#### Scenario: last_photometric_event devuelve True en el frame del evento
- **WHEN** se llama `detect(frame)` y ocurre un evento fotométrico
- **THEN** `last_photometric_event()` devuelve `True` hasta la siguiente llamada a `detect()`

#### Scenario: last_photometric_event devuelve False en frames normales
- **WHEN** se llama `detect(frame)` sin evento fotométrico
- **THEN** `last_photometric_event()` devuelve `False`

#### Scenario: El orchestrator guarda snapshot fondo_cambiado cuando ocurre el evento
- **WHEN** `last_photometric_event()` devuelve `True` tras una llamada a `detect()`
- **THEN** el `orchestrator` llama a `storage.save(frame, prefix="fondo_cambiado")` y NO publica alerta MQTT

#### Scenario: debug.py imprime el evento fotométrico y guarda snapshot categorizado
- **WHEN** el filtro fotométrico se activa
- **THEN** `debug.py` imprime `[!] CAMBIO FOTOMÉTRICO — reiniciando warmup (diff: X.X)` y guarda jpg con prefijo `fondo_cambiado_`
