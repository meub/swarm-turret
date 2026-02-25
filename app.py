from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit

from config import DEV_MODE, SERVER_HOST, SERVER_PORT
from turret.controller import TurretController
from camera.capture import Camera
from tracking.tracker import Tracker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Init hardware
turret = TurretController()

# Init camera
camera = Camera()
camera.start()

# Init tracker
tracker = Tracker(camera, turret)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(camera.generate_mjpeg(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('control', namespace='/control')
def handle_control(message):
    data = message['data']

    if 'position' in data:
        if not tracker.is_active():
            x = data['position'][0]
            y = data['position'][1]
            turret.set_position(x, y)
    elif 'A' in data:
        turret.fire()


@socketio.on('tracking', namespace='/control')
def handle_tracking(message):
    enabled = message.get('enabled', False)
    if enabled:
        tracker.start()
    else:
        tracker.stop()
    emit('tracking_status', {'active': tracker.is_active()})


@socketio.on_error_default
def default_error_handler(e):
    print(f"[SocketIO] Error: {e}")


if __name__ == '__main__':
    socketio.run(app, host=SERVER_HOST, port=SERVER_PORT,
                 debug=DEV_MODE, use_reloader=False,
                 allow_unsafe_werkzeug=True)
