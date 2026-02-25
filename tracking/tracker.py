import time
import threading

from config import (
    TRACKING_P_GAIN, TRACKING_DEAD_ZONE, TRACKING_FPS,
    CAMERA_WIDTH, CAMERA_HEIGHT,
)
from tracking.detector import HOGPersonDetector


class Tracker:
    def __init__(self, camera, turret):
        self._camera = camera
        self._turret = turret
        self._detector = HOGPersonDetector()
        self._active = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            if self._active:
                return
            self._active = True
        self._thread = threading.Thread(target=self._track_loop, daemon=True)
        self._thread.start()
        print("[Tracker] Started")

    def stop(self):
        with self._lock:
            self._active = False
        print("[Tracker] Stopped")

    def is_active(self):
        with self._lock:
            return self._active

    def _track_loop(self):
        interval = 1.0 / TRACKING_FPS
        center_x = CAMERA_WIDTH / 2
        center_y = CAMERA_HEIGHT / 2

        while self.is_active():
            start = time.time()

            frame = self._camera.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            detections = self._detector.detect(frame)

            if detections:
                # Pick largest detection (closest target)
                largest = max(detections, key=lambda d: d[2] * d[3])
                bx, by, bw, bh = largest

                # Center of detection
                det_cx = bx + bw / 2
                det_cy = by + bh / 2

                # Pixel error from frame center
                err_x = det_cx - center_x
                err_y = det_cy - center_y

                # Apply dead zone
                if abs(err_x) < TRACKING_DEAD_ZONE:
                    err_x = 0
                if abs(err_y) < TRACKING_DEAD_ZONE:
                    err_y = 0

                if err_x != 0 or err_y != 0:
                    cur_x, cur_y = self._turret.get_angles()
                    new_x = cur_x + err_x * TRACKING_P_GAIN
                    new_y = cur_y + err_y * TRACKING_P_GAIN
                    self._turret.set_angles(new_x, new_y)

            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)
