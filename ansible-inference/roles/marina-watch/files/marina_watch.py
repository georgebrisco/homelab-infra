#!/usr/bin/env python3
"""
Marina Watch — real-time object detection dashboard for the panoptes camera.

Pulls frames from an RTSP stream, runs YOLOv8 inference, and serves a live
web dashboard with annotated video, detection counts, and an activity log.

Designed for CPU-only inference on a homelab VM (8GB RAM, 2 cores).
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
from ultralytics import YOLO

# --- Configuration ---
RTSP_URL = os.environ.get('MARINA_RTSP_URL', 'rtsp://192.168.50.61:8554/cam')
MODEL_SIZE = os.environ.get('MARINA_MODEL', 'yolov8l')  # nano for CPU
CONFIDENCE = float(os.environ.get('MARINA_CONFIDENCE', '0.25'))
INFERENCE_INTERVAL = float(os.environ.get('MARINA_INTERVAL', '2.0'))  # seconds between inferences
WEB_PORT = int(os.environ.get('MARINA_PORT', '8080'))

# Classes of interest for a marina scene
MARINA_CLASSES = {
    'boat', 'person', 'bird', 'car', 'truck', 'bicycle', 'motorcycle',
    'dog', 'cat', 'airplane', 'kite', 'umbrella', 'backpack', 'tree'
    'surfboard', 'sports ball', 'frisbee'
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

# Detection statistics
detection_counts = Counter()     # all-time counts per class
activity_log = deque(maxlen=100) # recent detection events
hourly_counts = {}               # {hour_str: Counter}
fps_stats = {'capture': 0, 'inference': 0}
model_info = {'name': MODEL_SIZE, 'loaded': False}
stream_info = {'url': RTSP_URL, 'connected': False, 'resolution': ''}


def detection_worker():
    """Background thread: pull frames, run YOLO, update state."""
    global latest_frame, latest_annotated

    log.info('Loading YOLO model: %s', MODEL_SIZE)
    model = YOLO(MODEL_SIZE)
    model_info['loaded'] = True
    model_info['classes'] = len(model.names)
    log.info('Model loaded with %d classes', len(model.names))

    # Open RTSP stream
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

        # Read frame
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
        results = model(frame, conf=CONFIDENCE, verbose=False)
        inference_time = time.monotonic() - t1
        fps_stats['inference'] = 1.0 / max(inference_time, 0.001)

        # Process detections
        annotated = frame.copy()
        now = datetime.now()
        hour_key = now.strftime('%Y-%m-%d %H:00')
        if hour_key not in hourly_counts:
            hourly_counts[hour_key] = Counter()
            # Prune old hours (keep last 48)
            old_keys = sorted(hourly_counts.keys())[:-48]
            for k in old_keys:
                del hourly_counts[k]

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls[0])
                cls_name = model.names[cls_id]
                conf = float(box.conf[0])

                # Draw bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                color = class_color(cls_name)
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                label = '%s %.0f%%' % (cls_name, conf * 100)
                (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                cv2.rectangle(annotated, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
                cv2.putText(annotated, label, (x1 + 2, y1 - 4),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

                # Update statistics
                detection_counts[cls_name] += 1
                hourly_counts[hour_key][cls_name] += 1

                # Log notable detections (not every single one)
                if cls_name in MARINA_CLASSES:
                    activity_log.appendleft({
                        'time': now.strftime('%H:%M:%S'),
                        'class': cls_name,
                        'confidence': round(conf, 2),
                    })

        # Add overlay: timestamp + inference speed
        overlay_text = '%s | %.0fms inference' % (now.strftime('%H:%M:%S'), inference_time * 1000)
        cv2.putText(annotated, overlay_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        with frame_lock:
            latest_frame = frame
            latest_annotated = annotated

        # Throttle to configured interval
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
        .header .status { font-size: 13px; color: #888; }
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
                            '<span class="class-name">' + e.class + '</span> ' +
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
    log.info('RTSP:  %s', RTSP_URL)
    log.info('Model: %s', MODEL_SIZE)
    log.info('Web:   http://0.0.0.0:%d', WEB_PORT)

    # Start detection thread
    t = threading.Thread(target=detection_worker, daemon=True)
    t.start()

    # Start web server
    app.run(host='0.0.0.0', port=WEB_PORT, threaded=True)


if __name__ == '__main__':
    main()
