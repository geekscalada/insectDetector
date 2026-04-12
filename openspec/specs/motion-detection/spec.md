## Requirements

### Requirement: detector.detect transforma un frame BGR en una lista de detecciones
El módulo `detector` SHALL exponer `detect(frame: np.ndarray) -> list[Detection]` que aplica MOG2 con sustracción de sombras, pipeline morfológico configurable por `morph_operator`, y filtra contornos por área mínima (`min_area`) y dimensiones físicas máximas en cm (`max_width_cm`, `max_height_cm`, `pixels_per_cm`). El objeto MOG2 SHALL mantenerse como estado interno del módulo entre llamadas. El parámetro `mog2_shadow_threshold` SHALL pasarse a `createBackgroundSubtractorMOG2()` en la inicialización. El parámetro `morph_operator` (string: `open`, `close`, `erode`, `dilate`) SHALL mapearse a la constante OpenCV correspondiente y aplicarse al pipeline morfológico. El filtro de aspect ratio (`min_aspect_ratio`, `max_aspect_ratio`) ha sido eliminado — cualquier forma de contorno es válida.

`Detection` es un dataclass o namedtuple con campos: `bbox: tuple[int,int,int,int]` (x,y,w,h), `area: float`, `aspect_ratio: float`.

#### Scenario: Frame sin movimiento devuelve lista vacía
- **WHEN** se llama `detect(frame)` con un frame de fondo estático (sin diferencia respecto al modelo)
- **THEN** `detect()` devuelve `[]`

#### Scenario: Frame con insecto cuya área supera min_area y dimensiones dentro de máximos físicos devuelve detección
- **WHEN** se llama `detect(frame)` con un blob de área ≥ `min_area` y con `w ≤ max_width_px` O `h ≤ max_height_px`
- **THEN** `detect()` devuelve exactamente un elemento en la lista

#### Scenario: Blob de área menor que min_area se descarta
- **WHEN** se llama `detect(frame)` con un blob cuya área es menor que `min_area`
- **THEN** `detect()` devuelve `[]`

#### Scenario: Blob que excede ambas dimensiones físicas máximas se descarta
- **WHEN** se llama `detect(frame)` con un blob cuyo `w > max_width_px` Y `h > max_height_px`
- **THEN** `detect()` devuelve `[]`

#### Scenario: Blob cuadrado con área válida se acepta (aspect ratio ya no filtra)
- **WHEN** se llama `detect(frame)` con un blob cuadrado (aspect ratio ~1.0) cuya área ≥ `min_area` y dimensiones dentro de máximos
- **THEN** `detect()` devuelve el blob como detección válida

#### Scenario: Durante warm-up las detecciones se suprimen
- **WHEN** se llama `detect(frame)` en las primeras `warmup_frames` llamadas desde la inicialización del módulo
- **THEN** `detect()` devuelve `[]` independientemente del contenido del frame

#### Scenario: detect no realiza ninguna operación de I/O
- **WHEN** se llama `detect(frame)` con cualquier frame
- **THEN** no se escribe ningún fichero, no se emite ningún mensaje de red, y no se llama a ninguna función de `storage` ni `publisher`

#### Scenario: morph_operator open aplica erosión seguida de dilatación
- **WHEN** `config['detector']['morph_operator']` es `'open'`
- **THEN** el pipeline morfológico aplica `cv2.MORPH_OPEN`

#### Scenario: morph_operator close aplica dilatación seguida de erosión
- **WHEN** `config['detector']['morph_operator']` es `'close'`
- **THEN** el pipeline morfológico aplica `cv2.MORPH_CLOSE`

#### Scenario: mog2_shadow_threshold controla la clasificación de sombras
- **WHEN** `config['detector']['mog2_shadow_threshold']` está configurado a un valor float entre 0.0 y 1.0
- **THEN** el `BackgroundSubtractorMOG2` se inicializa con ese `shadowThreshold`

---

### Requirement: detector detecta cambios de luminancia inter-frame para suprimir falsos positivos fotométricos
El módulo `detector` SHALL mantener el frame gris del frame anterior como estado interno. En cada llamada a `detect()`, SHALL calcular `mean(abs(curr_gray − prev_gray))`. Si ese valor supera `config['detector']['photometric']['max_mean_diff']` y `config['detector']['photometric']['enable']` es `True`, SHALL devolver `[]` sin ejecutar MOG2 y SHALL pasar `learningRate=0` a `MOG2.apply()`. Cuando el frame es estable SHALL pasar el `learningRate` configurado a `MOG2.apply()`.

#### Scenario: Frame con cambio de luminancia superior al umbral devuelve lista vacía
- **WHEN** se llama `detect(frame)` y `mean(abs(curr_gray − prev_gray))` supera `photometric.max_mean_diff`
- **THEN** `detect()` devuelve `[]`

#### Scenario: Frame inestable no contamina el modelo de fondo
- **WHEN** se llama `detect(frame)` y el frame es fotométricamente inestable
- **THEN** `MOG2.apply()` se invoca con `learningRate=0`, de modo que el modelo de fondo no se actualiza con ese frame

#### Scenario: Frame estable usa el learningRate configurado
- **WHEN** se llama `detect(frame)` y `mean(abs(curr_gray − prev_gray))` está por debajo del umbral
- **THEN** `MOG2.apply()` se invoca con el valor de `photometric.learning_rate` (valor negativo = automático OpenCV)

#### Scenario: Primer frame no puede compararse y se deja pasar
- **WHEN** se llama `detect(frame)` por primera vez (no hay frame anterior almacenado)
- **THEN** el check de estabilidad se omite — `detect()` ejecuta el pipeline MOG2 normal

#### Scenario: Filtro desactivado no suprime detecciones por inestabilidad
- **WHEN** `config['detector']['photometric']['enable']` es `False`
- **THEN** el check de luminancia inter-frame no se ejecuta y `detect()` sigue el pipeline MOG2 sin modificar
