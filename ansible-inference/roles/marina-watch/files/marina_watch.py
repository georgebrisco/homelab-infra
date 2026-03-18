#!/usr/bin/env python3
"""
Marina Watch — real-time object detection dashboard for the panoptes camera.

Supports multiple backends:
  - YOLO (via ultralytics): set MARINA_MODEL to a yolo model name e.g. yolov8n.pt
  - RF-DETR (via rfdetr):   set MARINA_MODEL to rfdetr-base, rfdetr-large, rfdetr-nano, rfdetr-small

Pulls frames from an RTSP stream, runs inference, and serves a live
web dashboard with annotated video, detection counts, and an activity log.
"""

import os
import sys
import time
import json
import threading
import logging
from datetime import datetime, timedelta
from collections import Counter, deque

import cv2
import numpy as np
from flask import Flask, Response, render_template_string, jsonify

# --- Configuration ---
RTSP_URL = os.environ.get('MARINA_RTSP_URL', 'rtsp://192.168.50.61:8554/cam')
MODEL_SIZE = os.environ.get('MARINA_MODEL', 'rfdetr-base')
CONFIDENCE = float(os.environ.get('MARINA_CONFIDENCE', '0.35'))
INFERENCE_INTERVAL = float(os.environ.get('MARINA_INTERVAL', '2.0'))
IMGSZ = int(os.environ.get('MARINA_IMGSZ', '0'))  # 0 = model default, else e.g. 1280
WEB_PORT = int(os.environ.get('MARINA_PORT', '8080'))

# COCO class names (used by both YOLO and RF-DETR for COCO-pretrained models)
COCO_NAMES = {
    0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane',
    5: 'bus', 6: 'train', 7: 'truck', 8: 'fire hydrant', 9: 'stop sign',
    10: 'parking meter', 11: 'bench', 12: 'bird', 13: 'cat', 14: 'dog',
    15: 'horse', 16: 'sheep', 17: 'cow', 18: 'elephant', 19: 'bear',
    20: 'zebra', 21: 'giraffe', 22: 'backpack', 23: 'umbrella',
    24: 'handbag', 25: 'tie', 26: 'suitcase', 27: 'frisbee', 28: 'skis',
    29: 'snowboard', 30: 'sports ball', 31: 'kite', 32: 'baseball bat',
    33: 'baseball glove', 34: 'skateboard', 35: 'surfboard', 36: 'tennis racket',
    37: 'bottle', 38: 'wine glass', 39: 'cup', 40: 'fork', 41: 'knife',
    42: 'spoon', 43: 'bowl', 44: 'banana', 45: 'apple', 46: 'sandwich',
    47: 'orange', 48: 'broccoli', 49: 'carrot', 50: 'hot dog', 51: 'pizza',
    52: 'donut', 53: 'cake', 54: 'chair', 55: 'couch', 56: 'potted plant',
    57: 'bed', 58: 'dining table', 59: 'toilet', 60: 'tv', 61: 'laptop',
    62: 'mouse', 63: 'remote', 64: 'keyboard', 65: 'cell phone',
    66: 'microwave', 67: 'oven', 68: 'toaster', 69: 'sink',
    70: 'refrigerator', 71: 'book', 72: 'clock', 73: 'vase', 74: 'scissors',
    75: 'teddy bear', 76: 'hair drier', 77: 'toothbrush', 78: 'hair brush',
    79: 'banner', 80: 'blanket', 81: 'branch', 82: 'bridge', 83: 'building',
    84: 'bush', 85: 'cabinet', 86: 'cage', 87: 'cardboard', 88: 'carpet',
    89: 'ceiling', 90: 'tile ceiling', 91: 'cloth', 92: 'clothes',
    93: 'clouds', 94: 'counter', 95: 'cupboard', 96: 'curtain', 97: 'desk',
    98: 'dirt', 99: 'door', 100: 'fence',
}

MARINA_CLASSES = {
    'boat', 'person', 'bird', 'car', 'truck', 'bicycle', 'motorcycle',
    'dog', 'cat', 'airplane', 'kite', 'umbrella', 'backpack',
    'surfboard', 'sports ball', 'frisbee', 'bus', 'train',
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger('marina-watch')

# --- Global state ---
app = Flask(__name__)
latest_frame = None
latest_annotated = None
frame_lock = threading.Lock()

detection_counts = Counter()
activity_log = deque(maxlen=100)
hourly_counts = {}
fps_stats = {'capture': 0, 'inference': 0}
model_info = {'name': MODEL_SIZE, 'loaded': False, 'backend': 'unknown', 'imgsz': IMGSZ}
stream_info = {'url': RTSP_URL, 'connected': False, 'resolution': ''}


def is_rfdetr_model(name):
    return name.lower().startswith('rfdetr')


def load_model():
    """Load the appropriate model backend."""
    if is_rfdetr_model(MODEL_SIZE):
        import rfdetr
        model_map = {
            'rfdetr-nano': rfdetr.RFDETRNano,
            'rfdetr-small': rfdetr.RFDETRSmall,
            'rfdetr-base': rfdetr.RFDETRBase,
            'rfdetr-medium': rfdetr.RFDETRMedium,
            'rfdetr-large': rfdetr.RFDETRLarge,
        }
        model_key = MODEL_SIZE.lower()
        if model_key not in model_map:
            log.error('Unknown RF-DETR model: %s. Available: %s', MODEL_SIZE, list(model_map.keys()))
            sys.exit(1)
        log.info('Loading RF-DETR model: %s', MODEL_SIZE)
        model = model_map[model_key]()
        model_info['backend'] = 'rfdetr'
        model_info['classes'] = 80
        log.info('RF-DETR model loaded (COCO 80 classes)')
        return model
    else:
        from ultralytics import YOLO
        log.info('Loading YOLO model: %s', MODEL_SIZE)
        model = YOLO(MODEL_SIZE)
        model_info['backend'] = 'yolo'
        model_info['classes'] = len(model.names)
        log.info('YOLO model loaded with %d classes', len(model.names))
        return model


def run_inference_yolo(model, frame):
    """Run YOLO inference, return list of (cls_name, conf, x1, y1, x2, y2)."""
    kwargs = {'conf': CONFIDENCE, 'verbose': False}
    if IMGSZ > 0:
        kwargs['imgsz'] = IMGSZ
    results = model(frame, **kwargs)
    detections = []
    for result in results:
        if result.boxes is None:
            continue
        for box in result.boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append((cls_name, conf, x1, y1, x2, y2))
    return detections


def run_inference_rfdetr(model, frame):
    """Run RF-DETR inference, return list of (cls_name, conf, x1, y1, x2, y2)."""
    from PIL import Image
    # RF-DETR expects PIL Image or numpy array
    # Convert BGR (OpenCV) to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_frame)

    result = model.predict(pil_image, threshold=CONFIDENCE)

    detections = []
    if result.xyxy is not None and len(result.xyxy) > 0:
        for i in range(len(result.xyxy)):
            x1, y1, x2, y2 = map(int, result.xyxy[i])
            conf = float(result.confidence[i])
            cls_id = int(result.class_id[i])
            cls_name = COCO_NAMES.get(cls_id, 'class_%d' % cls_id)
            detections.append((cls_name, conf, x1, y1, x2, y2))
    return detections


def detection_worker():
    """Background thread: pull frames, run inference, update state."""
    global latest_frame, latest_annotated

    model = load_model()
    model_info['loaded'] = True

    use_rfdetr = is_rfdetr_model(MODEL_SIZE)

    cap = None
    reconnect_delay = 5

    while True:
        if cap is None or not cap.isOpened():
            log.info('Connecting to RTSP stream: %s', RTSP_URL)
            stream_info['connected'] = False
            cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if not cap.isOpened():
                log.warning('Failed to connect. Retrying in %ds...', reconnect_delay)
                time.sleep(reconnect_delay)
                continue
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            stream_info['connected'] = True
            stream_info['resolution'] = '%dx%d' % (w, h)
            log.info('Connected: %s', stream_info['resolution'])

        t0 = time.monotonic()
        ret, frame = cap.read()
        if not ret:
            log.warning('Frame read failed. Reconnecting...')
            cap.release()
            cap = None
            time.sleep(2)
            continue

        fps_stats['capture'] = 1.0 / max(time.monotonic() - t0, 0.001)

        # Run inference
        t1 = time.monotonic()
        if use_rfdetr:
            detections = run_inference_rfdetr(model, frame)
        else:
            detections = run_inference_yolo(model, frame)
        inference_time = time.monotonic() - t1
        fps_stats['inference'] = 1.0 / max(inference_time, 0.001)

        # Annotate frame
        annotated = frame.copy()
        now = datetime.now()
        hour_key = now.strftime('%Y-%m-%d %H:00')
        if hour_key not in hourly_counts:
            hourly_counts[hour_key] = Counter()
            old_keys = sorted(hourly_counts.keys())[:-48]
            for k in old_keys:
                del hourly_counts[k]

        for cls_name, conf, x1, y1, x2, y2 in detections:
            color = class_color(cls_name)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label = '%s %.0f%%' % (cls_name, conf * 100)
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            detection_counts[cls_name] += 1
            hourly_counts[hour_key][cls_name] += 1

            if cls_name in MARINA_CLASSES:
                activity_log.appendleft({
                    'time': now.strftime('%H:%M:%S'),
                    'class': cls_name,
                    'confidence': round(conf, 2),
                })

        # Overlay: model name, timestamp, inference time, detections in frame
        n_det = len(detections)
        overlay_line1 = '%s | %s | %.0fms | %d det' % (
            MODEL_SIZE, now.strftime('%H:%M:%S'), inference_time * 1000, n_det)
        cv2.putText(annotated, overlay_line1, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        with frame_lock:
            latest_frame = frame
            latest_annotated = annotated

        elapsed = time.monotonic() - t0
        sleep_time = max(0, INFERENCE_INTERVAL - elapsed)
        if sleep_time > 0:
            time.sleep(sleep_time)


def class_color(cls_name):
    """Deterministic color per class name."""
    h = hash(cls_name) % 180
    hsv = np.array([[[h, 255, 200]]], dtype=np.uint8)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
    return (int(bgr[0]), int(bgr[1]), int(bgr[2]))


def generate_mjpeg():
    """MJPEG stream generator for the /video_feed endpoint."""
    while True:
        with frame_lock:
            frame = latest_annotated
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.1)


# --- Web routes ---

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Marina Watch</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               background: #0a0a0f; color: #e0e0e0; }
        .header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                  padding: 16px 24px; display: flex; align-items: center; gap: 16px;
                  border-bottom: 1px solid #2a2a4a; }
        .header h1 { font-size: 24px; color: #4fc3f7; }
        .header .model-badge { font-size: 12px; background: #1a3a5c; color: #4fc3f7;
                              padding: 4px 10px; border-radius: 12px; font-weight: 600; }
        .header .status { font-size: 13px; color: #888; margin-left: auto; }
        .header .status .dot { display: inline-block; width: 8px; height: 8px;
                               border-radius: 50%; margin-right: 4px; }
        .dot.green { background: #4caf50; }
        .dot.red { background: #f44336; }
        .main { display: grid; grid-template-columns: 1fr 360px; gap: 16px;
                padding: 16px; max-height: calc(100vh - 70px); }
        .video-container { position: relative; background: #111; border-radius: 8px;
                          overflow: hidden; }
        .video-container img { width: 100%; display: block; }
        .sidebar { display: flex; flex-direction: column; gap: 12px;
                   overflow-y: auto; }
        .card { background: #12121f; border: 1px solid #2a2a4a; border-radius: 8px;
                padding: 14px; }
        .card h2 { font-size: 14px; color: #4fc3f7; margin-bottom: 10px;
                   text-transform: uppercase; letter-spacing: 1px; }
        .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .stat { text-align: center; padding: 8px; background: #1a1a2e;
                border-radius: 6px; }
        .stat .value { font-size: 28px; font-weight: bold; color: #4fc3f7; }
        .stat .label { font-size: 11px; color: #888; margin-top: 2px; }
        .detection-bar { display: flex; justify-content: space-between;
                        padding: 4px 0; border-bottom: 1px solid #1a1a2e; }
        .detection-bar .name { text-transform: capitalize; }
        .detection-bar .count { color: #4fc3f7; font-weight: bold; }
        .log-entry { font-size: 12px; padding: 4px 0;
                    border-bottom: 1px solid #1a1a2e; }
        .log-entry .time { color: #666; margin-right: 8px; font-family: monospace; }
        .log-entry .class-name { color: #4fc3f7; font-weight: 500; }
        .log-entry .conf { color: #888; font-size: 11px; }
        @media (max-width: 900px) {
            .main { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Marina Watch</h1>
        <span class="model-badge" id="model-badge">loading...</span>
        <div class="status" id="status">
            <span class="dot" id="status-dot"></span>
            <span id="status-text">Connecting...</span>
        </div>
    </div>
    <div class="main">
        <div class="video-container">
            <img src="/video_feed" alt="Live Feed">
        </div>
        <div class="sidebar">
            <div class="card">
                <h2>System</h2>
                <div class="stat-grid">
                    <div class="stat">
                        <div class="value" id="inf-speed">-</div>
                        <div class="label">Inference (ms)</div>
                    </div>
                    <div class="stat">
                        <div class="value" id="total-detections">0</div>
                        <div class="label">Total Detections</div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2>Detected Objects</h2>
                <div id="detection-list"></div>
            </div>
            <div class="card" style="flex: 1; overflow-y: auto;">
                <h2>Activity Log</h2>
                <div id="activity-log"></div>
            </div>
        </div>
    </div>
    <script>
        function updateStats() {
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    // Model badge
                    var badge = data.model.name;
                    if (data.model.backend) badge += ' (' + data.model.backend + ')';
                    document.getElementById('model-badge').textContent = badge;

                    // Status
                    const dot = document.getElementById('status-dot');
                    const text = document.getElementById('status-text');
                    if (data.stream.connected) {
                        dot.className = 'dot green';
                        text.textContent = 'Live (' + data.stream.resolution + ')';
                    } else {
                        dot.className = 'dot red';
                        text.textContent = 'Disconnected';
                    }

                    // Inference speed
                    if (data.fps.inference > 0) {
                        document.getElementById('inf-speed').textContent =
                            Math.round(1000 / data.fps.inference);
                    }

                    // Total detections
                    let total = Object.values(data.counts).reduce((a, b) => a + b, 0);
                    document.getElementById('total-detections').textContent =
                        total > 999 ? (total/1000).toFixed(1) + 'k' : total;

                    // Detection list
                    const sorted = Object.entries(data.counts)
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 12);
                    document.getElementById('detection-list').innerHTML =
                        sorted.map(([name, count]) =>
                            '<div class="detection-bar">' +
                            '<span class="name">' + name + '</span>' +
                            '<span class="count">' + count + '</span></div>'
                        ).join('');

                    // Activity log
                    document.getElementById('activity-log').innerHTML =
                        data.log.slice(0, 30).map(e =>
                            '<div class="log-entry">' +
                            '<span class="time">' + e.time + '</span>' +
                            '<span class="class-name">' + e['class'] + '</span> ' +
                            '<span class="conf">' + (e.confidence * 100).toFixed(0) + '%</span>' +
                            '</div>'
                        ).join('');
                })
                .catch(err => {
                    document.getElementById('status-dot').className = 'dot red';
                    document.getElementById('status-text').textContent = 'Error';
                });
        }
        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route('/video_feed')
def video_feed():
    return Response(generate_mjpeg(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stats')
def api_stats():
    return jsonify({
        'counts': dict(detection_counts),
        'log': list(activity_log),
        'fps': fps_stats,
        'stream': stream_info,
        'model': model_info,
    })


def main():
    log.info('Starting Marina Watch')
    log.info('RTSP:    %s', RTSP_URL)
    log.info('Model:   %s', MODEL_SIZE)
    log.info('ImgSize: %s', IMGSZ if IMGSZ > 0 else 'model default')
    log.info('Web:     http://0.0.0.0:%d', WEB_PORT)

    t = threading.Thread(target=detection_worker, daemon=True)
    t.start()

    app.run(host='0.0.0.0', port=WEB_PORT, threaded=True)


if __name__ == '__main__':
    main()
