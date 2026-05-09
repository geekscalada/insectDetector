## MODIFIED Requirements

### Requirement: museum_storage.save persiste un frame como JPEG en photo_historic con sufijo _museum
El módulo `src/storage/museum.py` SHALL exponer `save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path` que escribe el frame como JPEG en `output_dir/YYYY-MM-DD/YYYY-MM-DD-HH-MM-SS_museum.jpg`. SHALL crear el subdirectorio de día si no existe. SHALL propagar excepciones de escritura al llamador.

#### Scenario: save crea el fichero con el nuevo formato en photo_historic
- **WHEN** se llama `save(frame, datetime(2026, 5, 9, 14, 30, 0), "photo_historic/")`
- **THEN** existe el fichero `photo_historic/2026-05-09/2026-05-09-14-30-00_museum.jpg` y su tamaño es mayor que cero

#### Scenario: save crea el subdirectorio de día si no existe
- **WHEN** se llama `save(frame, timestamp, "photo_historic/")` y `photo_historic/2026-05-09/` no existe
- **THEN** el subdirectorio se crea y el fichero JPEG se escribe correctamente

### Requirement: museum_storage.purge elimina subdirectorios de día en photo_historic con antigüedad superior a retention_days
El módulo `src/storage/museum.py` SHALL exponer `purge(output_dir: str, retention_days: int) -> None` que elimina de forma recursiva cualquier subdirectorio de `output_dir` cuyo nombre tenga formato `YYYY-MM-DD` y cuya fecha sea anterior a `hoy - retention_days` días. SHALL ignorar silenciosamente subdirectorios con nombres que no sigan el formato `YYYY-MM-DD`. Si `output_dir` no existe, SHALL retornar sin error. Al operar sobre `photo_historic/`, la purga afecta también a JPEGs de detección de esa fecha — esto es intencional.

#### Scenario: purge elimina carpetas antiguas en photo_historic
- **GIVEN** que existen `photo_historic/2026-05-04/` y `photo_historic/2026-05-09/` y hoy es 2026-05-09
- **WHEN** se llama `purge("photo_historic/", retention_days=3)`
- **THEN** `photo_historic/2026-05-04/` se elimina y `photo_historic/2026-05-09/` permanece

#### Scenario: purge ignora directorios con nombre que no siga el formato YYYY-MM-DD
- **WHEN** existe `photo_historic/tmp/` junto a directorios de fecha
- **THEN** `purge` no elimina `photo_historic/tmp/` aunque sea antiguo

#### Scenario: purge no falla si output_dir no existe
- **WHEN** se llama `purge("photo_historic/", retention_days=3)` y `photo_historic/` no existe
- **THEN** la función retorna sin lanzar excepción
