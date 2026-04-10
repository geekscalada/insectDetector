## ADDED Requirements

### Requirement: detector.annotate dibuja bounding boxes sobre el frame y devuelve una copia anotada
El módulo `detector` SHALL exponer `annotate(frame: np.ndarray, detections: list[Detection]) -> np.ndarray` que devuelve una copia del frame con un rectángulo dibujado por cada detección usando las coordenadas `bbox` (x,y,w,h). SHALL NO mutar el frame original. Si `detections` está vacía, SHALL devolver una copia del frame sin modificaciones.

#### Scenario: Frame con una detección devuelve copia con un rectángulo
- **WHEN** se llama `annotate(frame, [detection])` con una detección cuyo `bbox` es `(10, 20, 50, 30)`
- **THEN** se devuelve un nuevo array numpy distinto al original, y los píxeles en la región del bounding box reflejan el rectángulo dibujado

#### Scenario: Frame vacío de detecciones devuelve copia sin modificar
- **WHEN** se llama `annotate(frame, [])`
- **THEN** se devuelve un nuevo array numpy con los mismos valores de píxel que el frame original

#### Scenario: El frame original no se muta
- **WHEN** se llama `annotate(frame, detections)` con cualquier lista de detecciones
- **THEN** el array `frame` original no es modificado — la función opera sobre una copia interna

#### Scenario: annotate no realiza ninguna operación de I/O
- **WHEN** se llama `annotate(frame, detections)` con cualquier frame y detecciones
- **THEN** no se escribe ningún fichero, no se emite ningún mensaje de red
