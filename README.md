
# The SwarmTurret

This is the web app for a 3D printed, websockets controlled Nerf turret with streaming video. It's powered by a Raspberry Pi 5 and three servos for the X axis, Y axis and firing control. See the turret in action [here](https://www.youtube.com/watch?v=2ocf1J5Sax4). It has a dedicated mobile and desktop web interface with streaming video that allows it to be controlled via WebSockets from a computer or mobile device. I've tested on Google Chrome on iOS, Mac and Windows but it is working for me on those platforms. This project was heavily inspired by [Tobias Weis' robotcontrol-javascript project](https://github.com/TobiasWeis/robotcontrol-javascript).

* [Build Guide](https://www.instructables.com/The-SwarmTurret-Wifi-Controlled-Foam-Dart-Turret/)
* [3D Parts](https://www.printables.com/model/1295975-swarmturret-v2-wifi-controlled-foam-dart-turret)

## Architecture

A single Flask-SocketIO server (`app.py`) handles both video streaming and WebSocket control on port 5000. Hardware control uses threading instead of multiprocessing. An autonomous tracking mode uses OpenCV HOG+SVM person detection with a proportional control loop to follow targets.

```
app.py              # Single server (video + control)
config.py           # All constants and settings
turret/             # Servo and trigger control
camera/             # Threaded video capture + MJPEG streaming
tracking/           # Autonomous person detection and tracking
static/             # JS (vanilla, no jQuery), CSS, images
templates/          # HTML
```

## Setup

    # Create Virtual Environment
    python3 -m venv .venv
    source .venv/bin/activate

    # Need to do this for some reason (https://stackoverflow.com/a/78935504/515367)
    pip install setuptools==57.5.0

    # Install packages
    pip install -r requirements.txt

    # Run app
    sh start.sh

## Dev Mode

You can develop and test the UI, video streaming, and tracking logic on your laptop without a Pi:

    SWARM_DEV=1 python app.py

This stubs out servo hardware (logs to console instead) and uses your laptop webcam. Open `http://localhost:5000` in your browser.

## Getting Started

This project assumes you have the hardware required and have plugged your servos into the servo HAT: X axis (pin 12), Y axis (pin 14), and trigger (pin 13). All pin assignments and angle ranges are configured in `config.py`.

The `keyboard-control.py` script makes it easy to test servo movement from a USB keyboard for calibration.

Start the server with `sh start.sh`. Stop with `sh stop.sh`.

## Controls

**Desktop:**
- **WASD** — Aim turret (velocity-based with friction)
- **Space** — Fire

**Mobile:**
- **Joystick** — Aim turret (touch-based)
- **Fire button** — Fire

**Autonomous Tracking:**
- Toggle via the checkbox in the UI
- Uses HOG person detection to track the largest detected target
- Manual aiming is disabled while tracking is active (fire still works)

## Configuration

All settings are in `config.py`:
- Servo pins, angle ranges, and inversion flags
- Trigger timing (fire duration, debounce)
- Camera settings (resolution, FPS, JPEG quality, stream FPS cap)
- Tracking parameters (P-gain, dead zone, detection FPS)
- Server host/port
- Dev mode flag

