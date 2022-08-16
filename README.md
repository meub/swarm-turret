# The SwarmTurret 

This is the web app for a 3D printed, websockets controlled Nerf turret with streaming video I built. It's powered by a Raspberry Pi 4 and three servos for the X axis, Y axis and firing control. More details on the build process can be found [here](https://alexmeub.com/building-a-web-controlled-nerf-turret/) and detail on the hardware and 3D printed parts can be found [here](https://www.printables.com/model/255165-swarmturret-web-controlled-foam-dart-turret).

This project was heavily inspired by [Tobias Weis' robotcontrol-javascript project](https://github.com/TobiasWeis/robotcontrol-javascript).

It has a dedicated mobile and desktop web interface with streaming video that allows it to be controlled via WebSockets from a computer or mobile device. I've tested on Google Chrome on iOS, Mac and Windows but it is working for me on those platforms.

## Requirements

* python, numpy, flask, adafruit_servokit, opencv-python
* Gunicorn
* Raspberry Pi 4 and [Adafruit Servo HAT](https://www.adafruit.com/product/2327)
* lots of other hardware and 3d printed parts listed [here](https://www.printables.com/model/255165-swarmturret-web-controlled-foam-dart-turret)

## Getting Started

This project assumes you have the hardware required and have plugged your servos into the servo HAT for X axis, Y axis, and trigger into pins 13, 12 and 14 respectively. I've included a script (keyboard-control.py) that makes it easy to test the servo movement from a USB keyboard. This is an important step for calibrating the min and max values for the X and Y axis servos. 

Due to issues with lag, this solution runs as two separate Flask apps. One for the Websockets control on port 5000 and one for the streaming video on port 6001. After calibrating your X and Y servos and adjusting the Min/Max values to be correct, you can start both web apps by running `sh start.sh`. You can run `sh stop.sh` to stop both apps.

## Pictures

![Nerf Turret V1](/nerf-turret-v1.png)

![Nerf Turret Web App](/nerf-turret-mobile.gif)