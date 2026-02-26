import cv2

from config import TRACKING_DOWNSCALE_WIDTH, TRACKING_DOWNSCALE_HEIGHT


class HOGPersonDetector:
    def __init__(self):
        self._hog = cv2.HOGDescriptor()
        self._hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def detect(self, frame):
        """Run detection on a frame. Returns list of (x, y, w, h) bounding boxes."""
        small = cv2.resize(frame, (TRACKING_DOWNSCALE_WIDTH, TRACKING_DOWNSCALE_HEIGHT))
        boxes, weights = self._hog.detectMultiScale(
            small, hitThreshold=0, winStride=(4, 4),
            padding=(8, 8), scale=1.05,
        )

        # Scale boxes back to original frame size
        scale_x = frame.shape[1] / TRACKING_DOWNSCALE_WIDTH
        scale_y = frame.shape[0] / TRACKING_DOWNSCALE_HEIGHT

        results = []
        for (x, y, w, h) in boxes:
            results.append((
                int(x * scale_x), int(y * scale_y),
                int(w * scale_x), int(h * scale_y),
            ))
        return results
