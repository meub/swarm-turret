#!/usr/bin/python
"""
Use a small REST server to control the turret.
"""

from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from multiprocessing import Queue
from adafruit_servokit import ServoKit
from engineio.payload import Payload

#Payload.max_decode_packets = 500
_debug = False

try:
    # Set up Adafruit servo controller object
    kit = ServoKit(channels=16)

    from turret.Servo import *

    # X-Axis, Servo Plugged in to Pin 12 in Servo HAT
    servo = Servo(Queue(), 12, kit, verbose=True)
    servo.start()

    # Y-Axis, Servo Plugged in to Pin 14 in Servo HAT
    servo2 = Servo(Queue(), 14, kit, verbose=True)
    servo2.start()

    # Trigger Servo, Plugged in to Pin 13 in Servo HAT
    from turret.Binary import *
    binary = Binary(Queue(), 13, kit, axis="A", verbose=True)
    binary.start()

except Exception as e:
    print("Could not import robot")
    print(e)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on_error_default
def default_error_handler(request):
    print("======================= ERROR")
    print(request.event["message"])
    print(request.event["args"])

@socketio.on('control', namespace='/control')
def control(message):
    data = message["data"]

    if "position" in data:
        x = data["position"][0]
        y = data["position"][1]
        if _debug: print("[Server] position: ", x, ",", y)
        servo.q.put(("position", x, y))
        servo2.q.put(("position", y, x))
    elif "A" in data:
        if _debug: print("[Server] A")
        binary.q.put(("A", 1, 0))


# Only used when running directly for development.
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)