# SwarmTurret — Project Guide

## Architecture

Single Flask-SocketIO server (`app.py`) on port 5000. No multiprocessing — uses `threading.Lock` for servo access and daemon threads for trigger/tracking. Deployed on Pi 5 via systemd (`swarm-turret.service`).

### File Structure
```
app.py                  # Flask-SocketIO server (routes, websocket handlers)
config.py               # All constants (pins, angles, timing, camera, tracking, dev mode)
swarm-turret.service    # systemd unit file for auto-start on boot
turret/
  servo.py              # Servo class — thread-safe angle control with input mapping
  trigger.py            # Trigger class — non-blocking threaded fire sequence
  controller.py         # TurretController facade — coordinates servos + trigger
camera/
  capture.py            # Threaded camera capture + MJPEG generator
tracking/
  detector.py           # HOG+SVM person detector (downscaled, weight-filtered)
  tracker.py            # Proportional control loop + scan patrol mode
static/
  js/app.js             # Vanilla JS (no jQuery) — WASD, joystick, tracking toggle
  css/styles.css        # Green CRT terminal theme
  img/crosshair.png     # Crosshair overlay
templates/
  index.html            # Single page — video feed, controls, tracking toggle
keyboard-control.py     # Standalone servo test/calibration script (pre-refactor, unchanged)
start.sh                # Runs `python app.py`
stop.sh                 # Kills all python processes
```

## Key Design Decisions

- **Threading over multiprocessing**: Servos use `threading.Lock` instead of `multiprocessing.Process` + `Queue`. Simpler, no IPC overhead.
- **Single server**: Video feed is same-origin (`/video_feed`), no hard-coded IPs, no CORS needed.
- **`async_mode='threading'`**: Avoids gevent monkey-patching conflicts with OpenCV threads.
- **Dev mode** (`SWARM_DEV=1`): Stubs out ServoKit hardware, uses laptop webcam. Full UI/tracking works without Pi.
- **Tracking blocks manual control**: When tracker is active, websocket position commands are ignored (fire still works).
- **`allow_unsafe_werkzeug=True`**: Required because Flask-SocketIO runs Werkzeug dev server, which refuses to start without `debug=True` unless this flag is set.
- **`PYTHONUNBUFFERED=1`** in systemd service: Required for print() output to appear in `journalctl` logs immediately.

## Hardware

- **Pi 5** with PCA9685 servo HAT (16-channel, Adafruit ServoKit)
- **Pin 12** (X-axis servo): range 40–180°, inverted
- **Pin 14** (Y-axis servo): range 0–180°, inverted
- **Pin 13** (trigger servo): fires at 100°, resets to 0°

## Servo Mapping

Input from websocket is -1..1. Mapping: `inverted → normalize to 0..1 → scale to angle range`.
- Pin 12: input -1 → 180°, input 0 → 110°, input 1 → 40°
- Pin 14: input -1 → 180°, input 0 → 90°, input 1 → 0°

**Important**: Error directions for tracking are negated (`err = -(det - center)`) because both servos are inverted.

## WebSocket Protocol

Namespace: `/control`

Client → Server:
- `control` event: `{data: {position: [x, y]}}` (normalized -1..1)
- `control` event: `{data: {A: 1}}` (fire)
- `tracking` event: `{enabled: true/false}`

Server → Client:
- `tracking_status` event: `{active: true/false}`

## Tracking System

### Detection
- **HOG+SVM** person detector via OpenCV (`cv2.HOGDescriptor`)
- Runs on downscaled 480x360 frames (~150-250ms per detection on Pi 5)
- Detections filtered by `MIN_WEIGHT = 0.3` to reduce false positives
- Parameters: `winStride=(4,4)`, `padding=(8,8)`, `scale=1.05`

### Control Loop
- **Proportional control**: `new_angle = current + error * P_GAIN` (P_GAIN = 0.03)
- **Dead zone**: 20px — ignores small errors to prevent jitter
- **Aim point**: Upper third of bounding box (head level, `by + bh * 0.3`)
- **Inverted errors**: Both X and Y errors negated to match inverted servos

### Scan/Patrol Mode
- Activates after 30 consecutive frames with no detection
- Sweeps X-axis back and forth at 0.5°/frame between servo limits
- Y-axis gradually returns to `SCAN_Y_ANGLE` (110°) at 1°/frame

### Current Status & Known Issues
- HOG detection is sporadic — works but misses many frames (~1 in 5-10 frames detects)
- Y-axis may still oscillate due to HOG bounding box instability between frames
- False positives reduced but not eliminated (furniture/objects sometimes detected)
- Consider: switching to a faster/more reliable detector (e.g., MobileNet SSD or MediaPipe) would significantly improve tracking quality

## Deployment

Pi is at `192.168.1.172` on the LAN. Deploy workflow:
```bash
# Push from laptop
git push

# On Pi
cd ~/swarm-turret && git pull
sudo cp swarm-turret.service /etc/systemd/system/  # only if service file changed
sudo systemctl daemon-reload                         # only if service file changed
sudo systemctl restart swarm-turret

# Check logs
journalctl -u swarm-turret -f
```

## Running

```bash
# On Pi (via systemd, auto-starts on boot)
sudo systemctl start swarm-turret

# On Pi (manual)
sh start.sh

# Dev mode (laptop, no hardware)
SWARM_DEV=1 python app.py
```

## Dependencies

Core: Flask, Flask-SocketIO, opencv-python, adafruit-circuitpython-servokit, numpy.
No jQuery, no gevent, no flask-cors.
