## ADDED Requirements

### Requirement: FrameSource entrega frames BGR desde picamera2
El módulo `capture` SHALL exponer un generador `FrameSource(fps: int)` que inicializa la Camera Module 2 NoIR con picamera2, configura la captura a la frecuencia `fps` indicada, y en cada iteración entrega un `numpy.ndarray` de shape `(H, W, 3)` dtype `uint8` en formato BGR.

#### Scenario: Frame tiene shape y dtype correctos
- **WHEN** se consume el primer frame de `FrameSource(10)`
- **THEN** el frame es un `numpy.ndarray` con `ndim == 3`, `shape[2] == 3` y `dtype == uint8`

#### Scenario: FrameSource libera la cámara al terminar
- **WHEN** se rompe el bucle de consumo o el generador se agota
- **THEN** picamera2 detiene la captura y libera el recurso de hardware (no queda proceso bloqueando la cámara)

#### Scenario: FrameSource usa la frecuencia configurada
- **WHEN** se crea `FrameSource(fps=10)`
- **THEN** la cámara se configura para capturar a 10 FPS — no se hardcodea ningún valor de frecuencia dentro del módulo
