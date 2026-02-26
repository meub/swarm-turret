import time
import threading

from config import (
    TRACKING_P_GAIN, TRACKING_DEAD_ZONE, TRACKING_FPS,
    CAMERA_WIDTH, CAMERA_HEIGHT,
    SERVO_X_MIN_ANGLE, SERVO_X_MAX_ANGLE,
    SCAN_SPEED, SCAN_Y_ANGLE,
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

        scan_dir = 1  # 1 = sweeping toward max, -1 = toward min
        frame_count = 0

        # Set Y to scan height on start
        self._turret.servo_y.set_angle(SCAN_Y_ANGLE)

        while self.is_active():
            start = time.time()

            frame = self._camera.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            detections = self._detector.detect(frame)
            detect_time = time.time() - start
            frame_count += 1

            if frame_count % 10 == 1:
                print(f"[Tracker] Frame {frame_count}: {len(detections)} detection(s), took {detect_time:.3f}s")

            if detections:
                print(f"[Tracker] Detected {len(detections)} target(s)")
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
                    print(f"[Tracker] err=({err_x:.0f},{err_y:.0f}) angle ({cur_x:.1f},{cur_y:.1f})->({new_x:.1f},{new_y:.1f})")
                    self._turret.set_angles(new_x, new_y)
            else:
                # No detection — scan back and forth
                cur_x, _ = self._turret.get_angles()
                new_x = cur_x + SCAN_SPEED * scan_dir

                # Reverse direction at limits
                if new_x >= SERVO_X_MAX_ANGLE:
                    new_x = SERVO_X_MAX_ANGLE
                    scan_dir = -1
                elif new_x <= SERVO_X_MIN_ANGLE:
                    new_x = SERVO_X_MIN_ANGLE
                    scan_dir = 1

                self._turret.set_angles(new_x, SCAN_Y_ANGLE)

            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)
