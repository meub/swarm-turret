#!/usr/bin/python

# Pi Nerf Turret Controller

import board
import busio
import adafruit_pca9685
import time
import keyboard
from adafruit_servokit import ServoKit

# Define object for servo control
kit = ServoKit(channels=16)

# Pins of each servo
x_axis = 13
y_axis = 12
trigger = 14

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
y_increment_unit = 2 # this determines speed of y axis movement
x_increment_unit = 5

# Utility Functions
def activate_trigger( number ):
	time.sleep(1)
	kit.servo[number].angle = 100
	time.sleep(0.3)
	# Set back to zero
	kit.servo[number].angle = 0

def reset_defaults():
	# Reset everything to known good values
	kit.servo[y_axis].angle = 50
	kit.servo[trigger].angle = trigger_min
	kit.continuous_servo[x_axis].throttle = 0

# Handle Keyup events separately for x axis control
# of continuous servos
#def on_key_release(key):
#	if "left" in key.name or "right" in key.name:
#		# Turn off
#		kit.continuous_servo[x_axis].throttle = 0

# Define the on release event
#keyboard.on_release(on_key_release, suppress=False)

# Main Loop
running = True

# Set Y to current position
print(kit.servo[y_axis].angle)
y_position = kit.servo[y_axis].angle	

# Reset Y Axis
# 100 should be straight ahead
kit.servo[y_axis].angle = 100
#running = False


while running:
	
	# Need to have this or else x axis continues after
    # key is released
	time.sleep(0.01)
	
	# Use while statements to prevent key repeat which is 
	# the desired behavior for controlling servos 
	# (we don't want servos to move after key is released)
	while keyboard.is_pressed("w"):
		y_position=y_position+y_increment_unit
		if( y_position > y_max ):
			print("Y is over max")
			print( y_position )
			y_position=y_position-y_increment_unit
		else:	
			kit.servo[y_axis].angle = y_position
			time.sleep(0.02)
			print( kit.servo[y_axis].angle )

	while keyboard.is_pressed("s"):
		y_position=y_position-y_increment_unit
		if( y_position < y_min ):
			print("Y is under min")
			print( y_position )
			y_position=y_position+y_increment_unit
		else:	
			kit.servo[y_axis].angle = y_position
			time.sleep(0.02)
			print( kit.servo[y_axis].angle )

	while keyboard.is_pressed("a"):
		#print("LEFT")
		#kit.continuous_servo[x_axis].throttle = -1
		x_position=x_position-x_increment_unit
		if( x_position < x_min ):
			print("X is under min")
			print( x_position )
			x_position=x_position+x_increment_unit
		else:	
			kit.servo[x_axis].angle = x_position
			time.sleep(0.02)
			print( kit.servo[x_axis].angle )	

	while keyboard.is_pressed("d"):
		#print("RIGHT")
		#kit.continuous_servo[x_axis].throttle = 1
		x_position=x_position+x_increment_unit
		if( x_position > x_max ):
			print("X is over max")
			print( x_position )
			x_position=x_position-x_increment_unit
		else:	
			kit.servo[x_axis].angle = x_position
			time.sleep(0.02)
			print( kit.servo[x_axis].angle )
		
	while keyboard.is_pressed(" "):
		print("SPACE")
		kit.servo[trigger].angle = 100
		time.sleep(0.3)
		kit.servo[trigger].angle = 0

	while keyboard.is_pressed("q"):
		print("Quitting...")
		kit.servo[y_axis].angle = 80
		running = False
		break

