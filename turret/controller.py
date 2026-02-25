from config import (
    DEV_MODE,
    SERVO_X_PIN, SERVO_Y_PIN, TRIGGER_PIN,
    SERVO_X_MIN_ANGLE, SERVO_X_MAX_ANGLE, SERVO_X_INVERTED,
    SERVO_Y_MIN_ANGLE, SERVO_Y_MAX_ANGLE, SERVO_Y_INVERTED,
)
from turret.servo import Servo
from turret.trigger import Trigger


class TurretController:
    def __init__(self):
        kit = None
        if not DEV_MODE:
            try:
                from adafruit_servokit import ServoKit
                kit = ServoKit(channels=16)
            except Exception as e:
                print(f"[Turret] Could not init ServoKit: {e}")

        self.servo_x = Servo(kit, SERVO_X_PIN,
                             SERVO_X_MIN_ANGLE, SERVO_X_MAX_ANGLE,
                             inverted=SERVO_X_INVERTED)
        self.servo_y = Servo(kit, SERVO_Y_PIN,
                             SERVO_Y_MIN_ANGLE, SERVO_Y_MAX_ANGLE,
                             inverted=SERVO_Y_INVERTED)
        self.trigger = Trigger(kit, TRIGGER_PIN)

        mode = "DEV" if DEV_MODE else "HARDWARE"
        print(f"[Turret] Initialized in {mode} mode")

    def set_position(self, x, y):
        """Set position from websocket -1..1 input."""
        self.servo_x.set_from_input(x)
        self.servo_y.set_from_input(y)

    def set_angles(self, x_angle, y_angle):
        """Set absolute angles (used by tracker)."""
        self.servo_x.set_angle(x_angle)
        self.servo_y.set_angle(y_angle)

    def get_angles(self):
        """Return current (x_angle, y_angle)."""
        return self.servo_x.get_angle(), self.servo_y.get_angle()

    def fire(self):
        self.trigger.fire()
