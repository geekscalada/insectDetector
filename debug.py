import cv2
import yaml
import numpy as np
import os
import time
from datetime import datetime
from src.capture import FrameSource
from src import detector

# Cargar configuración
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

print("Iniciando cámara en modo DEBUG...")
print(f"Resolución: {config['camera']['width']}x{config['camera']['height']}")
print(f"pixels_per_cm: {config['detector']['pixels_per_cm']}")
print("Filtros activos para Detección Válida:")
print(f" - Área mínima: {config['detector']['min_area']} px")
print(f" - Tamaño máximo: {config['detector']['max_width_cm']} cm ancho, {config['detector']['max_height_cm']} cm alto")
print(f" - Solidez mínima: {config['detector']['min_solidity']}")
print("-" * 50)

# Inicializar detector
detector.init(config['detector'])
out_dir = config['storage']['output_dir']
last_save_time = 0
last_double_save_time = 0

# Precompute physical size limits in pixels (same as detector module)
ppcm = config['detector']['pixels_per_cm']
max_width_px = config['detector']['max_width_cm'] * ppcm
max_height_px = config['detector']['max_height_cm'] * ppcm
min_solidity = config['detector']['min_solidity']

try:    
    for frame in FrameSource(config['camera']):
        # Mismo pipeline que el detector real para ver qué pasa por debajo
        curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        lr = -1
        if detector._prev_gray is not None and config['detector']['photometric']['enable']:
            mean_diff = np.mean(np.abs(curr_gray.astype(float) - detector._prev_gray.astype(float)))
            if mean_diff > config['detector']['photometric']['max_mean_diff']:
                print(f"[!] CAMBIO FOTOMÉTRICO — reiniciando warmup (diff: {mean_diff:.1f})")
                blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
                detector._mog2.apply(blurred_frame, learningRate=0)
                detector._prev_gray = curr_gray
                detector._frame_count = 0
                # Save photometric snapshot (no throttle — always save)
                os.makedirs(out_dir, exist_ok=True)
                ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                cv2.imwrite(os.path.join(out_dir, f"{ts}_fondo_cambiado.jpg"), frame)
                continue

        detector._prev_gray = curr_gray
        blurred_frame = cv2.GaussianBlur(frame, (11, 11), 0)
        mask = detector._mog2.apply(blurred_frame, learningRate=lr)
        
        if detector._frame_count <= config['detector']['warmup_frames']:
            detector._frame_count += 1
            if detector._frame_count % 10 == 0:
                print(f"Calibrando fondo... (Warmup {detector._frame_count}/{config['detector']['warmup_frames']})")
            continue

        _, fg_mask = cv2.threshold(mask, 254, 255, cv2.THRESH_BINARY)
        fg_mask = cv2.morphologyEx(fg_mask, detector._morph_op, detector._kernel, iterations=config['detector']['morph_iterations'])
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        valid_detections = []    # passed all filters (green)
        qualifying_bboxes = []   # passed min_area regardless of size/solidity (red or green)
        visible_contours = 0
        annotated_frame = frame.copy()
        
        for c in contours:
            area = cv2.contourArea(c)
            if area < (config['detector']['min_area'] / 3):
                continue

            visible_contours += 1
            x, y, w, h = cv2.boundingRect(c)
            if min(w, h) == 0:
                continue

            w_cm = w / ppcm
            h_cm = h / ppcm
            aspect_ratio = max(w, h) / min(w, h)
            solidity = area / (w * h)

            area_ok = area >= config['detector']['min_area']
            size_ok = not (w > max_width_px and h > max_height_px)
            solidity_ok = solidity >= min_solidity

            if area_ok:
                qualifying_bboxes.append((x, y, w, h))

            if area_ok and size_ok and solidity_ok:
                print(f"[✓] INSECTO DETECTADO -> Area: {area:.0f} px | {w_cm:.1f}cm × {h_cm:.1f}cm | Sol: {solidity:.2f}")
                valid_detections.append((x, y, w, h))
                color = (0, 255, 0)
                text = f"INSECTO | {w_cm:.1f}x{h_cm:.1f}cm s={solidity:.2f}"
            else:
                reason = []
                if not area_ok:
                    reason.append(f"A={area:.0f}px")
                if not size_ok:
                    reason.append(f"W={w_cm:.1f}cm>maxW AND H={h_cm:.1f}cm>maxH")
                if not solidity_ok:
                    reason.append(f"Sol={solidity:.2f}<{min_solidity}")
                print(f"[x] Objeto ignorado -> {' | '.join(reason)}")
                color = (0, 0, 255)
                text = " / ".join(reason)

            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(annotated_frame, text, (x, max(15, y-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        if visible_contours == 0:
            continue

        now = time.time()
        ts = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
        os.makedirs(out_dir, exist_ok=True)

        if len(qualifying_bboxes) > 1 and (now - last_double_save_time > 1.0):
            print(f"[!] DESECHADA DOUBLE ({len(qualifying_bboxes)} objetos qualifying)")
            cv2.imwrite(os.path.join(out_dir, f"{ts}_desechada_double.jpg"), annotated_frame)
            last_double_save_time = now
        elif len(valid_detections) == 1 and (now - last_save_time > 1.0):
            cv2.imwrite(os.path.join(out_dir, f"{ts}_debug.jpg"), annotated_frame)
            print(f"📸 Foto guardada: {ts}_debug.jpg")
            last_save_time = now
        elif len(qualifying_bboxes) == 0 and visible_contours > 0 and (now - last_save_time > 1.0):
            # Only sub-threshold contours — still useful to see
            cv2.imwrite(os.path.join(out_dir, f"{ts}_debug.jpg"), annotated_frame)
            last_save_time = now

        detector._last_had_detection = len(valid_detections) > 0
            
except KeyboardInterrupt:
    print("\nSaliendo del modo debug...")
