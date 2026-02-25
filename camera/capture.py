import time
import threading
import cv2

from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, CAMERA_FPS,
    JPEG_QUALITY, STREAM_FPS_CAP,
)


class Camera:
    def __init__(self):
        self._cap = None
        self._frame = None
        self._lock = threading.Lock()
        self._running = False

    def start(self):
        self._cap = cv2.VideoCapture(CAMERA_INDEX)
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self._cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)
        self._running = True

        t = threading.Thread(target=self._capture_loop, daemon=True)
        t.start()
        print(f"[Camera] Started (index={CAMERA_INDEX}, {CAMERA_WIDTH}x{CAMERA_HEIGHT})")

    def _capture_loop(self):
        while self._running:
            success, frame = self._cap.read()
            if success:
                with self._lock:
                    self._frame = frame

    def get_frame(self):
        """Return a copy of the latest frame, or None."""
        with self._lock:
            if self._frame is not None:
                return self._frame.copy()
        return None

    def generate_mjpeg(self):
        """Yield MJPEG frames with quality control and FPS cap."""
        interval = 1.0 / STREAM_FPS_CAP
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]

        while self._running:
            start = time.time()
            frame = self.get_frame()
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame, encode_params)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' +
                       jpeg.tobytes() + b'\r\n\r\n')

            elapsed = time.time() - start
            if elapsed < interval:
                time.sleep(interval - elapsed)

    def stop(self):
        self._running = False
        if self._cap is not None:
            self._cap.release()
