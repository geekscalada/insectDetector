## 1. Configuración — nueva sección museum en config.yaml

- [x] 1.1 Añadir sección `museum` a `config.yaml` con claves `interval_seconds` (int), `retention_days` (int) y `output_dir` (str)
- [x] 1.2 Documentar con comentarios inline en `config.yaml` el significado de cada clave y la estimación de uso de disco

## 2. Módulo storage — museum.py

- [x] 2.1 Crear `src/storage/museum.py`
- [x] 2.2 Implementar `save(frame: np.ndarray, timestamp: datetime, output_dir: str) -> Path` que crea el subdirectorio `output_dir/YYYY-MM-DD/` si no existe y escribe el JPEG con nombre `YYYY-MM-DD_HH-mm-ss.jpg`
- [x] 2.3 Implementar `purge(output_dir: str, retention_days: int) -> None` que elimina subdirectorios con nombre `YYYY-MM-DD` cuya fecha sea anterior a `hoy - retention_days` días; ignora nombres que no sigan el formato; no falla si `output_dir` no existe

## 3. Orchestrator — integración de museum snapshot

- [x] 3.1 Importar `from src.storage import museum as museum_storage` en `src/orchestrator/__init__.py`
- [x] 3.2 Antes de entrar al bucle, llamar a `museum_storage.purge(config['museum']['output_dir'], config['museum']['retention_days'])`
- [x] 3.3 Inicializar `last_museum_ts = None` antes del bucle
- [x] 3.4 En cada iteración del bucle, comprobar si `last_museum_ts is None` o si han transcurrido `>= interval_seconds` desde el último guardado
- [x] 3.5 Si la condición se cumple: llamar a `museum_storage.save(frame, now, config['museum']['output_dir'])` dentro de un bloque `try/except`, actualizar `last_museum_ts = now` solo si no hubo excepción, y registrar errores con `print`

## 4. Verificación

- [x] 4.1 Verificar `museum_storage.save` con frame sintético: comprobar que el fichero existe en la ruta correcta y tiene tamaño mayor que cero
- [x] 4.2 Verificar `museum_storage.purge`: crear carpetas de fecha artificiales, llamar a `purge` y comprobar que las antiguas se eliminan y las recientes permanecen
- [x] 4.3 Verificar que `purge` no lanza excepción si `output_dir` no existe
- [x] 4.4 Verificar que un error en `museum_storage.save` no interrumpe el bucle del orchestrator
