## MODIFIED Requirements

### Requirement: storage.save persiste un frame como JPEG con timestamp en photo_historic
El módulo `storage` SHALL exponer `save(frame: np.ndarray, timestamp: datetime, output_dir: str, prefix: str = "detection") -> Path` que escribe el frame como JPEG en `output_dir/YYYY-MM-DD/YYYY-MM-DD-HH-MM-SS_{prefix}.jpg`. SHALL crear el subdirectorio de día si no existe. SHALL propagar cualquier excepción de escritura al llamador.

#### Scenario: El fichero se crea en la ruta correcta con el nuevo formato
- **WHEN** se llama `save(frame, datetime(2026, 5, 9, 14, 30, 0), "photo_historic/", prefix="detection")`
- **THEN** existe el fichero `photo_historic/2026-05-09/2026-05-09-14-30-00_detection.jpg` y su tamaño es mayor que cero

#### Scenario: El subdirectorio de día se crea si no existe
- **WHEN** se llama `save(frame, timestamp, "photo_historic/")` y `photo_historic/2026-05-09/` no existe
- **THEN** el subdirectorio se crea y el fichero JPEG se escribe correctamente

#### Scenario: El prefijo se refleja correctamente en el nombre de fichero
- **WHEN** se llama `save(frame, timestamp, "photo_historic/", prefix="desechada_double")`
- **THEN** el fichero creado termina en `_desechada_double.jpg`

#### Scenario: Un error de escritura se propaga
- **WHEN** `output_dir` apunta a una ruta no escribible
- **THEN** `save` lanza una excepción — no la silencia
