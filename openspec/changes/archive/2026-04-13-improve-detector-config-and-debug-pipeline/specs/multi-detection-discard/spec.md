## ADDED Requirements

### Requirement: multi-detection-discard descarta frames con más de una detección válida
El `orchestrator` SHALL, tras recibir la lista de detecciones de `detector.detect()`, verificar si `len(detections) > 1`. Si es así, SHALL llamar a `storage.save(frame, prefix="desechada_double")` para guardar evidencia y NO publicar ninguna alerta MQTT. Esta lógica reside exclusivamente en el `orchestrator`.

#### Scenario: Frame con una sola detección sigue el flujo normal
- **WHEN** `detector.detect(frame)` devuelve exactamente una detección
- **THEN** el `orchestrator` continúa el flujo normal: guarda evidencia con prefijo estándar y publica alerta MQTT

#### Scenario: Frame con más de una detección se descarta con snapshot
- **WHEN** `detector.detect(frame)` devuelve dos o más detecciones
- **THEN** el `orchestrator` llama a `storage.save(frame, prefix="desechada_double")` y NO llama a `publisher.publish()`

#### Scenario: Frame sin detecciones no genera ningún guardado
- **WHEN** `detector.detect(frame)` devuelve lista vacía
- **THEN** el `orchestrator` no guarda ningún fichero ni publica nada

#### Scenario: debug.py muestra estado DESECHADA DOUBLE y lo registra en consola
- **WHEN** `detector.detect(frame)` en `debug.py` devuelve más de una detección
- **THEN** `debug.py` imprime `[!] DESECHADA DOUBLE (N objetos)` y guarda un JPEG con el sufijo `desechada_double_` con todos los bounding boxes anotados en naranja
