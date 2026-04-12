## ADDED Requirements

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
