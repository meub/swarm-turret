# SwarmTurret — Project Guide

## Architecture

Single Flask-SocketIO server (`app.py`) on port 5000. No multiprocessing — uses `threading.Lock` for servo access and daemon threads for trigger/tracking.

### File Structure
```
app.py                  # Flask-SocketIO server (routes, websocket handlers)
config.py               # All constants (pins, angles, timing, camera, tracking, dev mode)
turret/
  servo.py              # Servo class — thread-safe angle control with input mapping
  trigger.py            # Trigger class — non-blocking threaded fire sequence
  controller.py         # TurretController facade — coordinates servos + trigger
camera/
  capture.py            # Threaded camera capture + MJPEG generator
tracking/
  detector.py           # HOG+SVM person detector (downscaled for speed)
  tracker.py            # Proportional control loop — detection → error → servo correction
static/
  js/app.js             # Vanilla JS (no jQuery) — WASD, joystick, tracking toggle
  css/styles.css        # Green CRT terminal theme
  img/crosshair.png     # Crosshair overlay
templates/
  index.html            # Single page — video feed, controls, tracking toggle
keyboard-control.py     # Standalone servo test/calibration script
start.sh                # Runs `python app.py`
stop.sh                 # Kills all python processes
```

## Key Design Decisions

- **Threading over multiprocessing**: Servos use `threading.Lock` instead of `multiprocessing.Process` + `Queue`. Simpler, no IPC overhead.
- **Single server**: Video feed is same-origin (`/video_feed`), no hard-coded IPs, no CORS needed.
- **`async_mode='threading'`**: Avoids gevent monkey-patching conflicts with OpenCV threads.
- **Dev mode** (`SWARM_DEV=1`): Stubs out ServoKit hardware, uses laptop webcam. Full UI/tracking works without Pi.
- **Tracking blocks manual control**: When tracker is active, websocket position commands are ignored (fire still works).

## Hardware

- **Pi 5** with PCA9685 servo HAT (16-channel, Adafruit ServoKit)
- **Pin 12** (X-axis servo): range 40–180°, inverted
- **Pin 14** (Y-axis servo): range 0–180°, inverted
- **Pin 13** (trigger servo): fires at 100°, resets to 0°

## Servo Mapping

Input from websocket is -1..1. Mapping: `inverted → normalize to 0..1 → scale to angle range`.
- Pin 12: input -1 → 180°, input 0 → 110°, input 1 → 40°
- Pin 14: input -1 → 180°, input 0 → 90°, input 1 → 0°

## WebSocket Protocol

Namespace: `/control`

Client → Server:
- `control` event: `{data: {position: [x, y]}}` (normalized -1..1)
- `control` event: `{data: {A: 1}}` (fire)
- `tracking` event: `{enabled: true/false}`

Server → Client:
- `tracking_status` event: `{active: true/false}`

## Running

```bash
# On Pi
sh start.sh

# Dev mode (laptop, no hardware)
SWARM_DEV=1 python app.py
```

## Dependencies

Core: Flask, Flask-SocketIO, opencv-python, adafruit-circuitpython-servokit, numpy.
No jQuery, no gevent, no flask-cors.
