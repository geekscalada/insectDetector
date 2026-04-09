## 1. Configuración

- [x] 1.1 Añadir sección `orchestrator` a `config.yaml` con `capture_limit: 5`
- [x] 1.2 Verificar que `config.yaml` sigue siendo YAML válido tras el cambio

## 2. Módulo capture

- [x] 2.1 Implementar `src/capture/__init__.py` con el generador `FrameSource(fps: int)` usando picamera2, formato `BGR888`, liberando la cámara en `finally`
- [x] 2.2 Verificar que `FrameSource` importa sin error en un entorno sin cámara (la importación de picamera2 no debe fallar al importar el módulo, sólo al instanciar)

## 3. Módulo storage

- [x] 3.1 Implementar `src/storage/__init__.py` con `save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path`
- [x] 3.2 El nombre de fichero SHALL ser `YYYY-MM-DDTHH-MM-SS.jpg` (`:` reemplazados por `-`)
- [x] 3.3 `save` SHALL crear `output_dir` si no existe (`os.makedirs(..., exist_ok=True)`)
- [x] 3.4 Verificar `save` con un frame sintético: `np.zeros((480, 640, 3), dtype=np.uint8)` — comprobar que el fichero se crea y tiene tamaño > 0

## 4. Módulo orchestrator

- [x] 4.1 Implementar `src/orchestrator/__init__.py` con `run(config: dict) -> None`
- [x] 4.2 El bucle SHALL iterar `FrameSource` con `enumerate`, romper al llegar a `capture_limit`, guardar cada frame con `storage.save` y capturar excepciones de storage con `print` + continuar
- [x] 4.3 Verificar que `orchestrator` importa correctamente tras la implementación

## 5. Verificación en Raspberry Pi

- [ ] 5.1 Ejecutar `pip install -r requirements.txt` en la Pi
- [ ] 5.2 Ejecutar `python main.py` en la Pi y comprobar que aparecen exactamente 5 ficheros JPEG en `detections/`
- [ ] 5.3 Abrir uno de los JPEGs y confirmar que muestra imagen real de la cámara
