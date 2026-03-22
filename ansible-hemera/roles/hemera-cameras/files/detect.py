#!/usr/bin/env python3
"""Hemera: Hailo-8 accelerated object detection with direct camera capture.

Uses picamera2 for zero-copy frame capture from the IMX477, eliminating the
RTSP encode/decode round-trip. Frames go directly from the camera ISP to
Hailo inference. Serves an MJPEG dashboard on :8080.
"""
import cv2, numpy as np, threading, time, os, json
from flask import Flask, Response
from picamera2 import Picamera2
from hailo_platform import (HEF, VDevice, HailoStreamInterface,
    ConfigureParams, InputVStreamParams, OutputVStreamParams,
    InferVStreams, FormatType)

app = Flask(__name__)
MODEL_PATH = os.environ.get('MODEL_PATH', '/usr/share/hailo-models/yolov8s_h8.hef')
CONFIDENCE = float(os.environ.get('CONFIDENCE', '0.5'))
PORT = int(os.environ.get('PORT', '8080'))
CAM_WIDTH = int(os.environ.get('CAM_WIDTH', '2028'))
CAM_HEIGHT = int(os.environ.get('CAM_HEIGHT', '1520'))
CAM_ID = int(os.environ.get('CAM_ID', '0'))

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
stats = {'fps': 0, 'dets': [], 'total': 0,
         'infer_ms': 0, 'preprocess_ms': 0, 'postprocess_ms': 0, 'total_ms': 0,
         'capture_ms': 0, 'resolution': '', 'mode': 'direct dual-stream (ISP resize)'}

def run():
    global latest_frame

    # Init Hailo first to get model input dimensions
    hef = HEF(MODEL_PATH)
    dev = VDevice()
    params = ConfigureParams.create_from_hef(hef, interface=HailoStreamInterface.PCIe)
    ng = dev.configure(hef, params)[0]
    inp_params = InputVStreamParams.make(ng, quantized=True, format_type=FormatType.UINT8)
    out_params = OutputVStreamParams.make(ng, quantized=False, format_type=FormatType.FLOAT32)
    inp_info = hef.get_input_vstream_infos()[0]
    h, w = inp_info.shape[0], inp_info.shape[1]
    print(f'Model: {MODEL_PATH} input={w}x{h} UINT8')

    # Init camera with dual-stream: main for display, lores for inference
    cam = Picamera2(CAM_ID)
    config = cam.create_video_configuration(
        main={"size": (CAM_WIDTH, CAM_HEIGHT), "format": "RGB888"},
        lores={"size": (w, h), "format": "RGB888"},
        buffer_count=2
    )
    cam.configure(config)
    cam.start()
    print(f'Camera {CAM_ID}: main={CAM_WIDTH}x{CAM_HEIGHT}, lores={w}x{h} (ISP-resized)')

    fc, ft = 0, time.time()

    with ng.activate():
        with InferVStreams(ng, inp_params, out_params) as pipe:
            while True:
                # Dual-stream capture: ISP gives us both sizes simultaneously
                t0 = time.perf_counter()
                request = cam.capture_request()
                frame = request.make_array("main")   # 2028x1520 for display
                img = request.make_array("lores")     # 640x640 for Hailo — ISP-resized
                request.release()
                t_cap = (time.perf_counter() - t0) * 1000

                t_total = time.perf_counter()
                oh, ow = frame.shape[:2]
                stats['resolution'] = f'{ow}x{oh}'

                t_pre = 0.0  # no CPU resize needed — ISP did it

                # Inference on Hailo
                t0 = time.perf_counter()
                raw = pipe.infer({inp_info.name: np.expand_dims(img, 0)})
                t_inf = (time.perf_counter() - t0) * 1000

                # Postprocess + draw
                t0 = time.perf_counter()
                dets = []
                for name, out_list in raw.items():
                    batch = out_list[0]
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
                t_post = (time.perf_counter() - t0) * 1000
                t_tot = (time.perf_counter() - t_total) * 1000

                stats['dets'] = dets
                stats['total'] += len(dets)
                stats['capture_ms'] = round(t_cap, 1)
                stats['preprocess_ms'] = round(t_pre, 1)
                stats['infer_ms'] = round(t_inf, 1)
                stats['postprocess_ms'] = round(t_post, 1)
                stats['total_ms'] = round(t_tot, 1)

                # Convert RGB to BGR for JPEG encoding
                with frame_lock:
                    latest_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
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
<style>
  body { font-family: sans-serif; background: #1a1a2e; color: #eee; margin: 0; padding: 20px; }
  h1 { color: #e94560; margin-bottom: 10px; }
  .layout { display: flex; gap: 20px; flex-wrap: wrap; }
  .video { flex: 3; min-width: 640px; }
  .video img { width: 100%; border-radius: 8px; }
  .panel { flex: 1; min-width: 220px; }
  .card { background: #16213e; padding: 14px; border-radius: 8px; margin-bottom: 10px; }
  .card h3 { margin: 0 0 6px; color: #e94560; font-size: 0.85em; text-transform: uppercase; }
  .card .val { font-size: 1.4em; font-weight: bold; }
  .card .sub { font-size: 0.8em; color: #888; margin-top: 4px; }
  .dets { font-size: 0.9em; }
  .dets span { background: #0f3460; padding: 3px 8px; border-radius: 4px; margin: 2px; display: inline-block; }
  a { color: #e94560; }
</style>
</head><body>
<h1>Hemera &mdash; Hailo-8 Detection</h1>
<div class="layout">
  <div class="video"><img src="/stream"/></div>
  <div class="panel" id="stats"></div>
</div>
<script>
async function update() {
  try {
    const r = await fetch('/api/status');
    const s = await r.json();
    const p = document.getElementById('stats');
    p.innerHTML = `
      <div class="card"><h3>FPS</h3><div class="val">${s.fps}</div>
        <div class="sub">${s.resolution} (${s.mode})</div></div>
      <div class="card"><h3>Pipeline</h3><div class="val">${s.total_ms} ms</div>
        <div class="sub">Capture: ${s.capture_ms} ms<br>Preprocess: ${s.preprocess_ms} ms<br>Inference: ${s.infer_ms} ms<br>Postprocess: ${s.postprocess_ms} ms</div></div>
      <div class="card"><h3>Detections</h3><div class="val">${s.dets.length}</div>
        <div class="sub">Total since start: ${s.total}</div>
        <div class="dets">${s.dets.map(d => `<span>${d.label} ${Math.round(d.score*100)}%</span>`).join('')}</div></div>
    `;
  } catch(e) {}
}
update(); setInterval(update, 1000);
</script>
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
