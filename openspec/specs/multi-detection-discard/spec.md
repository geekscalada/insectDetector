## Requirements

### Requirement: multi-detection-discard descarta frames con más de un contorno qualifying
El `orchestrator` SHALL, tras recibir la lista de detecciones de `detector.detect()`, consultar `detector.last_qualifying_count()`. Si ese valor es mayor que 1, SHALL llamar a `storage.save(frame, prefix="desechada_double")` para guardar evidencia y NO publicar ninguna alerta MQTT. Un contorno qualifying es aquel que supera `min_area` con independencia de si pasa los filtros de tamaño físico o solidez. Esta lógica reside exclusivamente en el `orchestrator`.

#### Scenario: Frame con un solo contorno qualifying sigue el flujo normal
- **WHEN** `detector.last_qualifying_count()` devuelve 1 tras `detect(frame)`
- **THEN** el `orchestrator` continúa el flujo normal: guarda evidencia con prefijo estándar y publica alerta MQTT si procede

#### Scenario: Frame con más de un contorno qualifying se descarta con snapshot
- **WHEN** `detector.last_qualifying_count()` devuelve 2 o más tras `detect(frame)`
- **THEN** el `orchestrator` llama a `storage.save(frame, prefix="desechada_double")` y NO llama a `publisher.publish()`

#### Scenario: Frame sin contornos qualifying no genera ningún guardado
- **WHEN** `detector.last_qualifying_count()` devuelve 0 y `detect(frame)` devuelve lista vacía
- **THEN** el `orchestrator` no guarda ningún fichero ni publica nada

#### Scenario: debug.py muestra estado DESECHADA DOUBLE y lo registra en consola
- **WHEN** hay más de un contorno qualifying en el frame (verdes o rojos)
- **THEN** `debug.py` imprime `[!] DESECHADA DOUBLE (N objetos qualifying)` y guarda un JPEG con sufijo `desechada_double` con todos los bounding boxes anotados en sus colores originales
