import threading


class Servo:
    def __init__(self, kit, pin, min_angle, max_angle, inverted=False):
        self._kit = kit
        self._pin = pin
        self._min_angle = min_angle
        self._max_angle = max_angle
        self._inverted = inverted
        self._lock = threading.Lock()
        self._angle = (min_angle + max_angle) / 2

    def map_input(self, value):
        """Map normalized input (-1..1) to servo angle range."""
        if self._inverted:
            value = -value
        normalized = (value + 1) / 2  # -1..1 → 0..1
        return normalized * (self._max_angle - self._min_angle) + self._min_angle

    def set_from_input(self, value):
        """Map normalized -1..1 input and set angle."""
        angle = self.map_input(value)
        self.set_angle(angle)

    def set_angle(self, angle):
        """Set servo to an absolute angle, clamped to range."""
        angle = max(self._min_angle, min(self._max_angle, angle))
        with self._lock:
            self._angle = angle
            if self._kit is not None:
                self._kit.servo[self._pin].angle = angle

    def get_angle(self):
        with self._lock:
            return self._angle
