## Requirements

### Requirement: El filtro de estabilidad fotométrica compara luminancia entre frames consecutivos
El módulo `detector` SHALL mantener como estado interno el frame gris (`prev_gray`) del frame procesado anteriormente. En cada llamada SHALL convertir el frame actual a escala de grises y calcular la diferencia media absoluta pixel a pixel (`mean(abs(curr_gray − prev_gray))`). Cuando ese valor supera `config['detector']['photometric']['max_mean_diff']`, el frame SHALL considerarse fotométricamente inestable. El estado `prev_gray` SHALL actualizarse al final de cada llamada a `detect()`, independientemente de si el frame fue estable o inestable.

#### Scenario: Diferencia de luminancia por debajo del umbral no activa el filtro
- **WHEN** `mean(abs(curr_gray − prev_gray))` es menor o igual que `photometric.max_mean_diff`
- **THEN** el filtro no suprime detecciones y el pipeline MOG2 se ejecuta con normalidad

#### Scenario: Diferencia de luminancia por encima del umbral activa el filtro
- **WHEN** `mean(abs(curr_gray − prev_gray))` supera `photometric.max_mean_diff`
- **THEN** el frame se marca como inestable, `detect()` devuelve `[]` y `MOG2.apply()` se invoca con `learningRate=0`

#### Scenario: prev_gray se actualiza tras cada frame, estable o inestable
- **WHEN** se procesa cualquier frame (estable o inestable)
- **THEN** `prev_gray` se actualiza al gris del frame actual para que la comparación del siguiente frame sea correcta

#### Scenario: Primer frame inicializa prev_gray sin activar el filtro
- **WHEN** `prev_gray` no existe todavía (primera llamada tras la inicialización)
- **THEN** se inicializa `prev_gray` con el gris del frame actual y el pipeline MOG2 se ejecuta con normalidad — no se suprime el primer frame

#### Scenario: Filtro desactivado por configuración no calcula ni compara luminancia
- **WHEN** `config['detector']['photometric']['enable']` es `False`
- **THEN** el módulo no calcula `mean abs diff`, no actualiza `prev_gray` y el pipeline MOG2 opera como si el filtro no existiera
