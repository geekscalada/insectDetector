## ADDED Requirements

### Requirement: physical-size-calibration permite filtrar contornos por dimensiones físicas en cm
`config.yaml` SHALL exponer tres parámetros bajo `detector`: `pixels_per_cm` (float), `max_width_cm` (float) y `max_height_cm` (float). El módulo `detector` SHALL convertir estas dimensiones en píxeles (`max_width_px = max_width_cm * pixels_per_cm`, `max_height_px = max_height_cm * pixels_per_cm`) durante la inicialización y usarlas para filtrar contornos en `detect()`. Un contorno se rechaza si `w > max_width_px` Y `h > max_height_px` — es decir, se acepta si cumple al menos una dimensión física (ancho ≤ max_width_cm O alto ≤ max_height_cm).

#### Scenario: Contorno dentro de dimensiones físicas máximas se acepta
- **WHEN** se llama `detect(frame)` con un contorno cuyo bounding box `w ≤ max_width_px` O `h ≤ max_height_px`
- **THEN** el filtro físico no rechaza el contorno y el pipeline sigue aplicando los demás filtros

#### Scenario: Contorno que excede ambas dimensiones físicas se rechaza
- **WHEN** se llama `detect(frame)` con un contorno cuyo bounding box `w > max_width_px` Y `h > max_height_px`
- **THEN** el contorno se descarta y no aparece en la lista de detecciones devuelta

#### Scenario: pixels_per_cm de 0 provoca error en inicialización
- **WHEN** se llama `detector.init(config)` con `pixels_per_cm = 0`
- **THEN** `init()` lanza `ValueError` informando que `pixels_per_cm` debe ser positivo

#### Scenario: debug.py muestra dimensiones físicas de cada contorno
- **WHEN** `debug.py` anota un frame
- **THEN** cada contorno visible muestra su ancho y alto en cm calculados con `pixels_per_cm`, además del área en píxeles
