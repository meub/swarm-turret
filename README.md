# The SwarmTurret 

This is the web app for a 3D printed, websockets controlled Nerf turret with streaming video I built. It's powered by a Raspberry Pi 4 and three servos for the X axis, Y axis and firing control. More details on the hardware build can be found [here](https://alexmeub.com/building-a-web-controlled-nerf-turret/).

This project was heavily inspired by [Tobias Weis' robotcontrol-javascript project](https://github.com/TobiasWeis/robotcontrol-javascript).

It has a dedicated mobile and desktop web interface with streaming video that allows it to be controlled via WebSockets from a computer or mobile device. I've only really tested on Google Chrome on iOS, Mac and Windows but it is working for me on those platforms.

![Nerf Turret Prototype](/nerf-turret-mobile.gif)

I've also included a script (keyboard-control.py) that makes it easy to test the servo movement from a USB keyboard. This is an important step for calibrating the min and max values for the X and Y axis servos.

## Hardware Used

* Raspberry Pi 4 (I know these are hard to find nowadays!)
* [Adafruit Servo HAT](https://www.adafruit.com/product/2327)
* 3x [20KG High Torque Servos](https://www.amazon.com/gp/product/B076CNKQX4/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1)


