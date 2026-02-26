import os

# Dev mode — set SWARM_DEV=1 to stub hardware and use laptop webcam
DEV_MODE = os.environ.get("SWARM_DEV", "0") == "1"

# --- Servo pins ---
SERVO_X_PIN = 12
SERVO_Y_PIN = 14
TRIGGER_PIN = 13

# --- Servo ranges ---
SERVO_X_MIN_ANGLE = 40
SERVO_X_MAX_ANGLE = 180
SERVO_X_INVERTED = True

SERVO_Y_MIN_ANGLE = 0
SERVO_Y_MAX_ANGLE = 180
SERVO_Y_INVERTED = True

# --- Trigger timing ---
TRIGGER_FIRE_DURATION = 0.3    # seconds servo held at fire angle
TRIGGER_FIRE_ANGLE = 100
TRIGGER_RESET_ANGLE = 0
TRIGGER_DEBOUNCE = 0.2         # minimum seconds between fires

# --- Camera ---
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
JPEG_QUALITY = 70
STREAM_FPS_CAP = 20

# --- Tracking ---
TRACKING_P_GAIN = 0.15
TRACKING_DEAD_ZONE = 20        # pixels from center to ignore
TRACKING_FPS = 10
TRACKING_DOWNSCALE_WIDTH = 480
TRACKING_DOWNSCALE_HEIGHT = 360

# --- Server ---
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000
