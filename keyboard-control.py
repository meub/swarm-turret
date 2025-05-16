#!/usr/bin/python

# Pi Nerf Turret Controller using pynput

import time
from pynput import keyboard
from adafruit_servokit import ServoKit
import threading

# Define object for servo control
kit = ServoKit(channels=16)

# Pins of each servo
x_axis = 12
trigger = 13
y_axis = 14

# Position Variables
y_position = 100
x_position = 90
trigger_position = 0

# Limits
y_max = 160
y_min = 20
x_max = 180
x_min = 0
trigger_min = 0
y_increment_unit = 2
x_increment_unit = 5

# State
pressed_keys = set()
running = True

# Utility Functions
def activate_trigger(number):
    time.sleep(1)
    kit.servo[number].angle = 100
    time.sleep(0.3)
    kit.servo[number].angle = 0

def reset_defaults():
    kit.servo[y_axis].angle = 50
    kit.servo[trigger].angle = trigger_min
    kit.continuous_servo[x_axis].throttle = 0

def on_press(key):
    try:
        pressed_keys.add(key.char.lower())
    except AttributeError:
        if key == keyboard.Key.space:
            pressed_keys.add('space')

def on_release(key):
    try:
        pressed_keys.discard(key.char.lower())
    except AttributeError:
        if key == keyboard.Key.space:
            pressed_keys.discard('space')

    if key == keyboard.Key.esc:
        return False  # Stop listener

# Main control loop
def control_loop():
    global x_position, y_position, running

    kit.servo[y_axis].angle = y_position

    while running:
        time.sleep(0.01)

        if 'w' in pressed_keys:
            y_position += y_increment_unit
            if y_position <= y_max:
                kit.servo[y_axis].angle = y_position
                print(f"Y: {y_position}")
            else:
                y_position -= y_increment_unit

        if 's' in pressed_keys:
            y_position -= y_increment_unit
            if y_position >= y_min:
                kit.servo[y_axis].angle = y_position
                print(f"Y: {y_position}")
            else:
                y_position += y_increment_unit

        if 'a' in pressed_keys:
            x_position -= x_increment_unit
            if x_position >= x_min:
                kit.servo[x_axis].angle = x_position
                print(f"X: {x_position}")
            else:
                x_position += x_increment_unit

        if 'd' in pressed_keys:
            x_position += x_increment_unit
            if x_position <= x_max:
                kit.servo[x_axis].angle = x_position
                print(f"X: {x_position}")
            else:
                x_position -= x_increment_unit

        if 'space' in pressed_keys:
            print("Firing!")
            kit.servo[trigger].angle = 100
            time.sleep(0.3)
            kit.servo[trigger].angle = 0
            pressed_keys.discard('space')  # prevent repeat firing

        if 'q' in pressed_keys:
            print("Quitting...")
            kit.servo[y_axis].angle = 80
            running = False
            break

# Start the listener in a separate thread
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Run the control loop
control_thread = threading.Thread(target=control_loop)
control_thread.start()

# Wait for threads to complete
listener.join()
control_thread.join()