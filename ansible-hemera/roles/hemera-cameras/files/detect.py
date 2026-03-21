#!/usr/bin/env python3
"""
hemera-detect: Hailo-accelerated object detection dashboard.
Captures frames from local RTSP stream (cam0), runs YOLOv8 on Hailo-8,
serves annotated MJPEG + web dashboard.
"""
import cv2
import numpy as np
import threading
import time
import os
import json
from datetime import datetime
from flask import Flask, Response, render_template_string
from hailo_platform import HEF, VDevice, ConfigureParams, InferVStreams, InputVStreamParams, OutputVStreamParams, FormatType

app = Flask(__name__)

# Config from environment
RTSP_URL = os.environ.get('RTSP_URL', 'rtsp://127.0.0.1:8554/cam0')
MODEL_PATH = os.environ.get('MODEL_PATH', '/usr/share/hailo-models/yolov8s_h8l.hef')
CONFIDENCE = float(os.environ.get('CONFIDENCE', '0.5'))
PORT = int(os.environ.get('PORT', '8080'))

# COCO class names
COCO_NAMES = [
    'person','bicycle','car','motorcycle','airplane','bus','train','truck','boat',
    'traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat',
    'dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack',
    'umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball',
    'kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket',
    'bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple',
    'sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair',
    'couch','potted plant','bed','dining table','toilet','tv','laptop','mouse',
    'remote','keyboard','cell phone','microwave','oven','toaster','sink',
    'refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush'
]

# Shared state
frame_lock = threading.Lock()
latest_frame = None
detections = []
det_lock = threading.Lock()
stats = {'fps': 0, 'total_detections': 0, 'start_time': time.time()}

def capture_and_detect():
    global latest_frame, detections
    
    # Init Hailo
    hef = HEF(MODEL_PATH)
    target = VDevice()
    configure_params = ConfigureParams.create_from_hef(hef, interface=HailoRTStreamInterface.PCIe)
    network_group = target.configure(hef, configure_params)[0]
    network_group_params = network_group.create_params()
    
    input_vstreams_params = InputVStreamParams.make(network_group, quantized=False, format_type=FormatType.FLOAT32)
    output_vstreams_params = OutputVStreamParams.make(network_group, quantized=False, format_type=FormatType.FLOAT32)
    
    input_vstream_info = hef.get_input_vstream_infos()[0]
    h, w = input_vstream_info.shape[0], input_vstream_info.shape[1]
    
    cap = cv2.VideoCapture(RTSP_URL)
    if not cap.isOpened():
        print(f'ERROR: Cannot open {RTSP_URL}')
        return
    
    frame_count = 0
    fps_start = time.time()
    
    with InferVStreams(network_group, input_vstreams_params, output_vstreams_params) as pipeline:
        while True:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                cap.release()
                cap = cv2.VideoCapture(RTSP_URL)
                continue
            
            orig_h, orig_w = frame.shape[:2]
            resized = cv2.resize(frame, (w, h))
            input_data = np.expand_dims(resized.astype(np.float32) / 255.0, axis=0)
            
            input_dict = {input_vstream_info.name: input_data}
            raw_output = pipeline.infer(input_dict)
            
            # Parse detections from output
            current_dets = []
            for name, output in raw_output.items():
                output = output[0]  # remove batch dim
                if len(output.shape) == 2:
                    for det in output:
                        if len(det) >= 6:
                            y1, x1, y2, x2, score, class_id = det[:6]
                            if score >= CONFIDENCE:
                                class_id = int(class_id)
                                label = COCO_NAMES[class_id] if class_id < len(COCO_NAMES) else f'class_{class_id}'
                                # Scale back to original frame
                                bx1 = int(x1 * orig_w)
                                by1 = int(y1 * orig_h)
                                bx2 = int(x2 * orig_w)
                                by2 = int(y2 * orig_h)
                                current_dets.append({
                                    'label': label, 'score': float(score),
                                    'box': (bx1, by1, bx2, by2)
                                })
                                cv2.rectangle(frame, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                                cv2.putText(frame, f'{label} {score:.2f}',
                                          (bx1, by1 - 8), cv2.FONT_HERSHEY_SIMPLEX,
                                          0.6, (0, 255, 0), 2)
            
            with det_lock:
                detections = current_dets
                stats['total_detections'] += len(current_dets)
            
            with frame_lock:
                latest_frame = frame.copy()
            
            frame_count += 1
            elapsed = time.time() - fps_start
            if elapsed >= 1.0:
                stats['fps'] = frame_count / elapsed
                frame_count = 0
                fps_start = time.time()

def generate_mjpeg():
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.05)
                continue
            _, jpeg = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(0.033)

DASHBOARD_HTML = '''<!DOCTYPE html>
<html><head><title>Hemera Detection</title>
<style>
  body { font-family: sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
  h1 { color: #e94560; }
  .container { display: flex; gap: 20px; flex-wrap: wrap; }
  .video { flex: 2; min-width: 640px; }
  .video img { width: 100%; border-radius: 8px; }
  .sidebar { flex: 1; min-width: 250px; }
  .stat { background: #16213e; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
  .stat h3 { margin: 0 0 5px; color: #e94560; }
</style>
</head><body>
<h1>Hemera — Hailo Detection Dashboard</h1>
<div class=container>
  <div class=video><img src=/stream /></div>
  <div class=sidebar>
    <div class=stat><h3>Model</h3>YOLOv8s on Hailo-8</div>
    <div class=stat><h3>Camera</h3>Pi HQ (IMX477)</div>
    <div class=stat><h3>Confidence</h3>{{ confidence }}</div>
  </div>
</div>
</body></html>'''

@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML, confidence=CONFIDENCE)

@app.route('/stream')
def stream():
    return Response(generate_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detections')
def api_detections():
    with det_lock:
        return json.dumps({'detections': detections, 'fps': stats['fps']})

if __name__ == '__main__':
    from hailo_platform import HailoRTStreamInterface
    t = threading.Thread(target=capture_and_detect, daemon=True)
    t.start()
    app.run(host='0.0.0.0', port=PORT, threaded=True)
