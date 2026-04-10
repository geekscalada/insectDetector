## ADDED Requirements

### Requirement: config.yaml documenta cada parámetro con comentarios inline en español
Cada parámetro de `config.yaml` SHALL tener uno o más comentarios YAML (`#`) inmediatamente encima o en la misma línea que describan: qué controla el parámetro, el rango de valores recomendado, y el efecto de subir o bajar el valor.

#### Scenario: El loader PyYAML no se ve afectado por los comentarios
- **WHEN** se carga `config.yaml` con `yaml.safe_load()`
- **THEN** el dict resultante contiene exactamente los mismos pares clave-valor que antes de añadir los comentarios, sin claves ni valores adicionales

#### Scenario: Cada parámetro tiene comentario descriptivo
- **WHEN** se inspeciona el fichero `config.yaml`
- **THEN** cada clave de primer y segundo nivel tiene al menos una línea de comentario `#` adyacente que describe su comportamiento
