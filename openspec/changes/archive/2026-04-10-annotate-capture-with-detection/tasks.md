## 1. Módulo detector — función annotate

- [x] 1.1 Añadir `annotate(frame: np.ndarray, detections: list[Detection]) -> np.ndarray` en `src/detector/__init__.py` que hace `frame.copy()`, llama a `cv2.rectangle` por cada detección usando el `bbox` (x,y,w,h), y devuelve el frame anotado
- [x] 1.2 Verificar que el frame original no se muta (test manual con array numpy sintético)
- [x] 1.3 Verificar que con `detections=[]` se devuelve una copia del frame sin rectángulos

## 2. Módulo orchestrator — integración de annotate

- [x] 2.1 En el punto del bucle donde se llama a `storage.save`, insertar `annotated = detector.annotate(frame, detections)` y pasar `annotated` a `storage.save` en lugar del `frame` original
- [x] 2.2 Verificar que el bucle sigue funcionando con una ejecución manual breve (o con frames sintéticos si no hay hardware disponible)
