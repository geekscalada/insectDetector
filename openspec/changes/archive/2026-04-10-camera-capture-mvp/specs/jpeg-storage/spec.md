## ADDED Requirements

### Requirement: storage.save persiste un frame como JPEG con timestamp
El módulo `storage` SHALL exponer `save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path` que escribe el frame como JPEG en `output_dir` con nombre derivado del timestamp. SHALL crear `output_dir` si no existe. SHALL propagar cualquier excepción de escritura al llamador.

#### Scenario: El fichero se crea en la ruta correcta
- **WHEN** se llama `save(frame, datetime(2026, 4, 9, 12, 0, 0, 123456), "detections/")`
- **THEN** existe el fichero `detections/2026-04-09T12-00-00.123456.jpg` y su tamaño es mayor que cero

#### Scenario: El directorio se crea si no existe
- **WHEN** se llama `save(frame, timestamp, "detections/subdir/")` y `detections/subdir/` no existe
- **THEN** el directorio se crea y el fichero JPEG se escribe correctamente

#### Scenario: Un error de escritura se propaga
- **WHEN** `output_dir` apunta a una ruta no escribible
- **THEN** `save` lanza una excepción — no la silencia
