#!/usr/bin/env python3
"""
Daily timelapse capture for panoptes camera.

Captures frames from the local RTSP stream at a configurable interval,
from civil dawn to one hour after sunset. At the end of the capture window,
stitches frames into an MP4 timelapse and stores it on TrueNAS via NFS.

Sunrise/sunset times are calculated daily using the astral library.
"""

import os
import sys
import time
import logging
import subprocess
import shutil
from datetime import datetime, timedelta, date
from pathlib import Path

from astral import LocationInfo
from astral.sun import sun

# --- Configuration (overridable via environment) ---
LATITUDE = float(os.environ.get('TIMELAPSE_LAT', '38.98'))
LONGITUDE = float(os.environ.get('TIMELAPSE_LON', '-76.49'))
TIMEZONE = os.environ.get('TIMELAPSE_TZ', 'America/New_York')
LOCATION_NAME = os.environ.get('TIMELAPSE_LOCATION', 'Marina')

RTSP_URL = os.environ.get('TIMELAPSE_RTSP_URL', 'rtsp://127.0.0.1:8554/cam')
CAPTURE_INTERVAL = int(os.environ.get('TIMELAPSE_INTERVAL', '30'))  # seconds
OUTPUT_FPS = int(os.environ.get('TIMELAPSE_FPS', '30'))
FRAME_DIR = Path(os.environ.get('TIMELAPSE_FRAME_DIR', '/tmp/timelapse_frames'))
OUTPUT_DIR = Path(os.environ.get('TIMELAPSE_OUTPUT_DIR', '/mnt/truenas/media/timelapse'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger('timelapse')


def get_capture_window(target_date=None):
    """Calculate today's capture window: civil dawn -> sunset + 1 hour."""
    if target_date is None:
        target_date = date.today()

    location = LocationInfo(LOCATION_NAME, 'US', TIMEZONE, LATITUDE, LONGITUDE)
    s = sun(location.observer, date=target_date, tzinfo=TIMEZONE)

    start = s['dawn']          # civil dawn (~30 min before sunrise)
    end = s['sunset'] + timedelta(hours=1)

    return start, end, s


def capture_frame(frame_path):
    """Capture a single JPEG frame from the RTSP stream."""
    try:
        result = subprocess.run(
            [
                'ffmpeg', '-y',
                '-rtsp_transport', 'tcp',
                '-i', RTSP_URL,
                '-frames:v', '1',
                '-q:v', '2',
                '-update', '1',
                frame_path
            ],
            capture_output=True, timeout=15
        )
        return result.returncode == 0 and os.path.exists(frame_path)
    except subprocess.TimeoutExpired:
        log.warning('Frame capture timed out')
        return False
    except Exception as e:
        log.warning('Frame capture failed: %s', e)
        return False


def stitch_timelapse(frame_dir, output_path, fps=30):
    """Stitch captured JPEG frames into an MP4 timelapse."""
    log.info('Stitching timelapse -> %s', output_path)
    glob_pattern = str(frame_dir / '*.jpg')
    result = subprocess.run(
        [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-pattern_type', 'glob',
            '-i', glob_pattern,
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            str(output_path)
        ],
        capture_output=True, timeout=600
    )
    if result.returncode != 0:
        stderr = result.stderr.decode()[-500:]
        log.error('ffmpeg stitch failed: %s', stderr)
        return False
    return True


def main():
    today = date.today()
    start_time, end_time, sun_info = get_capture_window(today)
    now = datetime.now(start_time.tzinfo)

    log.info('Date:    %s', today)
    log.info('Dawn:    %s', sun_info["dawn"].strftime("%H:%M"))
    log.info('Sunrise: %s', sun_info["sunrise"].strftime("%H:%M"))
    log.info('Sunset:  %s', sun_info["sunset"].strftime("%H:%M"))
    log.info('Capture: %s -> %s', start_time.strftime("%H:%M"), end_time.strftime("%H:%M"))
    log.info('Now:     %s', now.strftime("%H:%M"))

    # If we've already passed today's window, exit
    if now > end_time:
        log.info('Capture window has passed for today. Exiting.')
        sys.exit(0)

    # Wait for capture window to begin
    if now < start_time:
        wait_seconds = (start_time - now).total_seconds()
        log.info('Waiting %.0f minutes for dawn...', wait_seconds / 60)
        time.sleep(wait_seconds)

    # Prepare frame directory
    frame_dir = FRAME_DIR / today.isoformat()
    frame_dir.mkdir(parents=True, exist_ok=True)
    log.info('Frame directory: %s', frame_dir)

    # Capture loop
    frame_count = 0
    consecutive_failures = 0
    max_failures = 10

    while True:
        now = datetime.now(start_time.tzinfo)
        if now > end_time:
            log.info('Capture window ended.')
            break

        frame_path = str(frame_dir / ('frame_%06d.jpg' % frame_count))
        loop_start = time.monotonic()

        if capture_frame(frame_path):
            frame_count += 1
            consecutive_failures = 0
            if frame_count % 60 == 0:
                log.info('Captured %d frames...', frame_count)
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                log.error('%d consecutive failures - aborting capture.', max_failures)
                break

        # Sleep until next capture, accounting for capture time
        elapsed = time.monotonic() - loop_start
        sleep_time = max(0, CAPTURE_INTERVAL - elapsed)
        time.sleep(sleep_time)

    log.info('Capture complete: %d frames', frame_count)

    if frame_count < 10:
        log.warning('Too few frames for a timelapse. Cleaning up.')
        shutil.rmtree(frame_dir, ignore_errors=True)
        sys.exit(1)

    # Stitch into timelapse
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / ('timelapse_%s.mp4' % today.isoformat())
    if stitch_timelapse(frame_dir, output_file, OUTPUT_FPS):
        size_mb = output_file.stat().st_size / (1024 * 1024)
        duration = frame_count / OUTPUT_FPS
        log.info('Timelapse saved: %s (%.1f MB, %.0fs at %dfps)', output_file, size_mb, duration, OUTPUT_FPS)
    else:
        log.error('Failed to create timelapse video.')

    # Clean up frames
    shutil.rmtree(frame_dir, ignore_errors=True)
    log.info('Frames cleaned up. Done.')


if __name__ == '__main__':
    main()
