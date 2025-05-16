
# The SwarmTurret 

This is the web app for a 3D printed, websockets controlled Nerf turret with streaming video. It's powered by a Raspberry Pi 5 and three servos for the X axis, Y axis and firing control. See the turret in action [here](https://www.youtube.com/watch?v=2ocf1J5Sax4). It has a dedicated mobile and desktop web interface with streaming video that allows it to be controlled via WebSockets from a computer or mobile device. I've tested on Google Chrome on iOS, Mac and Windows but it is working for me on those platforms. This project was heavily inspired by [Tobias Weis' robotcontrol-javascript project](https://github.com/TobiasWeis/robotcontrol-javascript).

* [Build Guide](https://www.instructables.com/The-SwarmTurret-Wifi-Controlled-Foam-Dart-Turret/)
* [3D Parts](https://www.printables.com/model/1295975-swarmturret-v2-wifi-controlled-foam-dart-turret)

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

## Getting Started

This project assumes you have the hardware required and have plugged your servos into the servo HAT: X axis (pin 12), Y axis (pin 14), and trigger (pin 13). I've included a script (keyboard-control.py) that makes it easy to test the servo movement from a USB keyboard. This is an important step for calibrating the min and max values for the X and Y axis servos. 

Due to issues with lag, this solution runs as two separate Flask apps. One for the Websockets control on port 5000 and one for the streaming video on port 6001. After calibrating your X and Y servos and adjusting the Min/Max values to be correct, you can start both web apps by running `sh start.sh`. You can run `sh stop.sh` to stop both apps.


