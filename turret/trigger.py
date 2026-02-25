import time
import threading

from config import (
    TRIGGER_FIRE_ANGLE, TRIGGER_RESET_ANGLE,
    TRIGGER_FIRE_DURATION, TRIGGER_DEBOUNCE,
)


class Trigger:
    def __init__(self, kit, pin):
        self._kit = kit
        self._pin = pin
        self._last_fire = 0
        self._lock = threading.Lock()

    def fire(self):
        now = time.time()
        with self._lock:
            if now - self._last_fire < TRIGGER_DEBOUNCE:
                return
            self._last_fire = now

        t = threading.Thread(target=self._fire_sequence, daemon=True)
        t.start()

    def _fire_sequence(self):
        try:
            if self._kit is not None:
                self._kit.servo[self._pin].angle = TRIGGER_FIRE_ANGLE
                time.sleep(TRIGGER_FIRE_DURATION)
                self._kit.servo[self._pin].angle = TRIGGER_RESET_ANGLE
            else:
                print(f"[DEV] Fire on pin {self._pin}")
        except Exception as e:
            print(f"[Trigger] Could not fire: {e}")
