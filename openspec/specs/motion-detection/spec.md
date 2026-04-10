## Requirements

### Requirement: detector.detect transforma un frame BGR en una lista de detecciones
El módulo `detector` SHALL exponer `detect(frame: np.ndarray) -> list[Detection]` que aplica MOG2 con sustracción de sombras, pipeline morfológico configurable por `morph_operator`, y filtra contornos por área y aspect ratio usando los parámetros de `config['detector']`. El objeto MOG2 SHALL mantenerse como estado interno del módulo entre llamadas. El parámetro `mog2_shadow_threshold` SHALL pasarse a `createBackgroundSubtractorMOG2()` en la inicialización. El parámetro `morph_operator` (string: `open`, `close`, `erode`, `dilate`) SHALL mapearse a la constante OpenCV correspondiente y aplicarse al pipeline morfológico.

`Detection` es un dataclass o namedtuple con campos: `bbox: tuple[int,int,int,int]` (x,y,w,h), `area: float`, `aspect_ratio: float`.

#### Scenario: Frame sin movimiento devuelve lista vacía
- **WHEN** se llama `detect(frame)` con un frame de fondo estático (sin diferencia respecto al modelo)
- **THEN** `detect()` devuelve `[]`

#### Scenario: Frame con insecto en rango válido devuelve una detección
- **WHEN** se llama `detect(frame)` con un frame que contiene un blob de área entre `min_area` y `max_area` y aspect ratio entre `min_aspect_ratio` y `max_aspect_ratio`
- **THEN** `detect()` devuelve exactamente un elemento en la lista con `area` y `aspect_ratio` dentro de los rangos configurados

#### Scenario: Blob fuera de rango de área se descarta
- **WHEN** se llama `detect(frame)` con un blob cuya área es menor que `min_area` o mayor que `max_area`
- **THEN** `detect()` devuelve `[]`

#### Scenario: Blob con aspect ratio fuera de rango se descarta
- **WHEN** se llama `detect(frame)` con un blob cuadrado (aspect ratio ~1.0)
- **THEN** `detect()` devuelve `[]` cuando el rango configurado es [1.5, 3.0]

#### Scenario: Durante warm-up las detecciones se suprimen
- **WHEN** se llama `detect(frame)` en las primeras `warmup_frames` llamadas desde la inicialización del módulo
- **THEN** `detect()` devuelve `[]` independientemente del contenido del frame

#### Scenario: detect no realiza ninguna operación de I/O
- **WHEN** se llama `detect(frame)` con cualquier frame
- **THEN** no se escribe ningún fichero, no se emite ningún mensaje de red, y no se llama a ninguna función de `storage` ni `publisher`

#### Scenario: morph_operator open aplica erosión seguida de dilatación
- **WHEN** `config['detector']['morph_operator']` es `'open'`
- **THEN** el pipeline morfológico aplica `cv2.MORPH_OPEN` (mismo comportamiento que antes del cambio)

#### Scenario: morph_operator close aplica dilatación seguida de erosión
- **WHEN** `config['detector']['morph_operator']` es `'close'`
- **THEN** el pipeline morfológico aplica `cv2.MORPH_CLOSE`

#### Scenario: mog2_shadow_threshold controla la clasificación de sombras
- **WHEN** `config['detector']['mog2_shadow_threshold']` está configurado a un valor float entre 0.0 y 1.0
- **THEN** el `BackgroundSubtractorMOG2` se inicializa con ese `shadowThreshold`
