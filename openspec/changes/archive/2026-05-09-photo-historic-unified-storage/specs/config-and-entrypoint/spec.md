## MODIFIED Requirements

### Requirement: config.yaml contiene photo_historic.output_dir como única ruta de almacenamiento de imágenes
El fichero `config.yaml` SHALL contener la clave `photo_historic.output_dir` (string de ruta) como única fuente de verdad para el directorio de todas las imágenes guardadas (frames de detección y frames de museo). Las claves `storage.output_dir` y `museum.output_dir` SHALL eliminarse del fichero de configuración.

#### Scenario: config.yaml contiene la sección photo_historic con output_dir
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `photo_historic.output_dir` con valor de ruta string

#### Scenario: config.yaml NO contiene storage.output_dir
- **WHEN** se lee `config.yaml`
- **THEN** el documento NO contiene la clave `storage.output_dir`

#### Scenario: config.yaml NO contiene museum.output_dir
- **WHEN** se lee `config.yaml`
- **THEN** el documento NO contiene la clave `museum.output_dir`

#### Scenario: museum.interval_seconds y museum.retention_days permanecen en la sección museum
- **WHEN** se lee `config.yaml`
- **THEN** el documento contiene `museum.interval_seconds` y `museum.retention_days` con sus valores actuales
