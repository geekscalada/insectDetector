## Requirements

### Requirement: el orchestrator guarda un frame de museo al arrancar y cada interval_seconds
El `orchestrator` SHALL mantener un estado `last_museum_ts` inicializado a `None`. En cada iteración del bucle de detección SHALL comprobar si `last_museum_ts is None OR (now - last_museum_ts).total_seconds() >= config['museum']['interval_seconds']`. Si la condición se cumple, SHALL llamar a `museum_storage.save(frame, now, config['museum']['output_dir'])` y actualizar `last_museum_ts = now`. Los errores de `museum_storage.save` SHALL capturarse, registrarse con `print` y no interrumpir el bucle.

### Requirement: el orchestrator purga el archivo de museo al arrancar
El `orchestrator` SHALL llamar a `museum_storage.purge(config['museum']['output_dir'], config['museum']['retention_days'])` una única vez, antes de entrar al bucle de detección.

#### Scenario: se guarda el primer frame al arrancar
- **WHEN** el orchestrator entra al bucle y `last_museum_ts` es `None`
- **THEN** `museum_storage.save` se llama en la primera iteración, independientemente del estado del detector

#### Scenario: se guarda un frame cada interval_seconds
- **WHEN** han transcurrido al menos `interval_seconds` desde el último guardado de museo
- **THEN** `museum_storage.save` se llama con el frame actual y `last_museum_ts` se actualiza

#### Scenario: no se guarda un frame de museo antes de que expire el intervalo
- **WHEN** han transcurrido menos de `interval_seconds` desde el último guardado de museo
- **THEN** `museum_storage.save` no se llama en esa iteración

#### Scenario: un error de museum_storage no interrumpe el bucle
- **WHEN** `museum_storage.save` lanza una excepción
- **THEN** el orchestrator registra el error con `print`, no actualiza `last_museum_ts`, y continúa el bucle normalmente

#### Scenario: la purga se ejecuta una sola vez al arrancar
- **WHEN** el orchestrator inicia
- **THEN** `museum_storage.purge` se llama exactamente una vez, antes de la primera iteración del bucle
