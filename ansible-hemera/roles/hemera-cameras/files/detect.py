#!/usr/bin/env python3
"""Hemera: Hailo-8 accelerated object detection dashboard."""
import cv2, numpy as np, threading, time, os, json
from flask import Flask, Response, render_template_string
from hailo_platform import (HEF, VDevice, HailoStreamInterface,
    ConfigureParams, InputVStreamParams, OutputVStreamParams,
    InferVStreams, FormatType)

app = Flask(__name__)
RTSP_URL = os.environ.get('RTSP_URL', 'rtsp://127.0.0.1:8554/cam0')
MODEL_PATH = os.environ.get('MODEL_PATH', '/usr/share/hailo-models/yolov8s_h8.hef')
CONFIDENCE = float(os.environ.get('CONFIDENCE', '0.5'))
PORT = int(os.environ.get('PORT', '8080'))

COCO = ['person','bicycle','car','motorcycle','airplane','bus','train','truck','boat',
    'traffic light','fire hydrant','stop sign','parking meter','bench','bird','cat',
    'dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack',
    'umbrella','handbag','tie','suitcase','frisbee','skis','snowboard','sports ball',
    'kite','baseball bat','baseball glove','skateboard','surfboard','tennis racket',
    'bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple',
    'sandwich','orange','broccoli','carrot','hot dog','pizza','donut','cake','chair',
    'couch','potted plant','bed','dining table','toilet','tv','laptop','mouse',
    'remote','keyboard','cell phone','microwave','oven','toaster','sink',
    'refrigerator','book','clock','vase','scissors','teddy bear','hair drier','toothbrush']

frame_lock = threading.Lock()
latest_frame = None
stats = {'fps': 0, 'dets': [], 'total': 0}

def run():
    global latest_frame
    hef = HEF(MODEL_PATH)
    dev = VDevice()
    params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
    ng = dev.configure(hef, params)[0]
    inp_params = InputVStreamParams.make(ng, quantized=True, format_type=FormatType.UINT8)
    out_params = OutputVStreamParams.make(ng, quantized=False, format_type=FormatType.FLOAT32)
    inp_info = hef.get_input_vstream_infos()[0]
    h, w = inp_info.shape[0], inp_info.shape[1]
    print(f'Model: {MODEL_PATH} input={w}x{h} UINT8')

    cap = cv2.VideoCapture(RTSP_URL)
    fc, ft = 0, time.time()

    with ng.activate():
        with InferVStreams(ng, inp_params, out_params) as pipe:
            while True:
                ret, frame = cap.read()
                if not ret:
                    time.sleep(0.5)
                    cap.release()
                    cap = cv2.VideoCapture(RTSP_URL)
                    continue

                oh, ow = frame.shape[:2]
                img = cv2.resize(frame, (w, h)).astype(np.uint8)
                raw = pipe.infer({inp_info.name: np.expand_dims(img, 0)})

                dets = []
                for name, out_list in raw.items():
                    batch = out_list[0]  # list of 80 per-class arrays
                    for cls_id, cls_dets in enumerate(batch):
                        arr = np.array(cls_dets)
                        if arr.size == 0:
                            continue
                        if arr.ndim == 1:
                            arr = arr.reshape(1, -1)
                        for det_idx in range(arr.shape[0]):
                            y1, x1, y2, x2, score = arr[det_idx, :5]
                            if score < CONFIDENCE:
                                continue
                            label = COCO[cls_id] if cls_id < len(COCO) else f'c{cls_id}'
                            bx1, by1 = int(x1*ow), int(y1*oh)
                            bx2, by2 = int(x2*ow), int(y2*oh)
                            cv2.rectangle(frame, (bx1,by1), (bx2,by2), (0,255,0), 2)
                            cv2.putText(frame, f'{label} {score:.0%}', (bx1,by1-8),
                                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)
                            dets.append({'label': label, 'score': round(float(score),2)})

                stats['dets'] = dets
                stats['total'] += len(dets)
                with frame_lock:
                    latest_frame = frame.copy()
                fc += 1
                if time.time() - ft >= 1:
                    stats['fps'] = round(fc/(time.time()-ft), 1)
                    fc = 0
                    ft = time.time()

def gen():
    while True:
        with frame_lock:
            if latest_frame is None:
                time.sleep(0.05)
                continue
            _, jpg = cv2.imencode('.jpg', latest_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n'
        time.sleep(0.033)

HTML = '''<!DOCTYPE html><html><head><title>Hemera</title>
<style>body{font-family:sans-serif;background:#1a1a2e;color:#eee;margin:0;padding:20px}
h1{color:#e94560}.v{max-width:960px}img{width:100%;border-radius:8px}</style>
</head><body><h1>Hemera &mdash; Hailo-8 Detection</h1>
<div class="v"><img src="/stream"/></div>
<p>YOLOv8s on Hailo-8 | Pi HQ Camera (IMX477) | <a href="/api/status" style="color:#e94560">API</a></p>
</body></html>'''

@app.route('/')
def index(): return HTML
@app.route('/stream')
def stream(): return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/api/status')
def api(): return json.dumps(stats)

if __name__ == '__main__':
    threading.Thread(target=run, daemon=True).start()
    app.run(host='0.0.0.0', port=PORT, threaded=True)
