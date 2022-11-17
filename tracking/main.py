#!/usr/bin/env python
#
# Project: Video Streaming with face recognition
# Author: agametov [at] gmail [dot] com>
# Date: 2016/02/11

from importlib import import_module
import time, os, math, cv2, board, busio
import adafruit_pca9685
from flask import Flask, render_template, Response
from multiprocessing import Process, Queue
from camera import VideoCamera
from adafruit_servokit import ServoKit

# Define object for servo control
kit = ServoKit(channels=16)

# Pins of each servo
x_axis = 13
y_axis = 12
trigger = 14

# Position Variables
y_position = 50
x_position = 100
trigger_position = 0

# Limits
y_max = 160
y_min = 20
x_max = 180
x_min = 0

trigger_min = 0
y_increment_unit = 2 # this determines speed of y axis movement
x_increment_unit = 2

# Utility Functions
def activate_trigger( number ):
	time.sleep(1)
	kit.servo[number].angle = 100
	time.sleep(0.3)
	# Set back to zero
	kit.servo[number].angle = 0

# Set Y to current position
#y_position = kit.servo[y_axis].angle	

print(kit.servo[y_axis].angle)

# Reset Y Axis
# 100 should be straight ahead
kit.servo[y_axis].angle = y_position

# Reset X Axis
kit.servo[x_axis].angle = x_position

print ("INITIALIZE AT X: " + str(x_position) + " Y:" + str(y_position) )

#running = False

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):

    global x_axis
    global y_axis
    global x_position
    global y_position
    global x_increment_unit
    global y_increment_unit
    global kit

    while True:
        obj = camera.get_frame()
        
        # Render frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + obj[0] + b'\r\n\r\n')

        # Get coords and adjust here?
        if (obj[1] > 0):
            
            time.sleep(0.1)
            #print(obj[1],obj[2],obj[3],obj[4])

            x = obj[1]
            y = obj[2]
            w = obj[3]
            h = obj[4]

            # Center point
            center_x = x + (w/2)
            center_y = y + (h/2)
            
            print("center")
            print( center_x )
            print( center_y )

            #print("servos")
            #print( kit.servo[x_axis].angle )
            #print( kit.servo[y_axis].angle )
            
            #### Y AXIS ####

            # Move DOWN, camera is too damn high
            if( center_y < 235 ):
                print("Move DOWN")
                y_position=y_position-y_increment_unit
                if( y_position > y_max ):
                    print("Y is over max")
                    print( y_position )
                    y_position=y_position-y_increment_unit
                else:
                    print("ypos: " + str(y_position))
                    kit.servo[y_axis].angle = y_position
                    #time.sleep(0.02)

            # Move UP, camera is too low
            elif( center_y > 245 ):
                print("Move UP")
                y_position=y_position+y_increment_unit
                if( y_position < y_min ):
                    print("Y is under min")
                    print( y_position )
                    y_position=y_position+y_increment_unit
                else:	
                    print("ypos: " + str(y_position))
                    kit.servo[y_axis].angle = y_position
                    #time.sleep(0.02)

            #### X AXIS ####
            
            # Move RIGHT, camera is too far left
            if( center_x > 325 ):
                print("Move RIGHT")
                #kit.continuous_servo[x_axis].throttle = -1
                x_position=x_position-x_increment_unit
                if( x_position < x_min ):
                    print("X is under min")
                    print( x_position )
                    x_position=x_position+x_increment_unit
                else:
                    print("xpos: " + str(x_position))
                    kit.servo[x_axis].angle = x_position
                    #time.sleep(0.02)
                    print( kit.servo[x_axis].angle )	
             
            # Move LEFT, camera is too far right
            elif( center_x < 315 ):
                print("Move LEFT")
                #kit.continuous_servo[x_axis].throttle = 1
                x_position=x_position+x_increment_unit
                if( x_position > x_max ):
                    print("X is over max")
                    print( x_position )
                    x_position=x_position-x_increment_unit
                else:
                    print("xpos: " + str(x_position))
                    kit.servo[x_axis].angle = x_position
                    #time.sleep(0.02)
                    print( kit.servo[x_axis].angle )
            
            '''
                x = 326.5 / 640
                y = 450.5 / 480

                Y Axis
                NewMin = 40
                NewMax = 180
            

            #y_position=y_position-y_increment_unit
            #kit.servo[y_axis].angle = y_position

            #x_position=x_position-x_increment_unit
            #kit.servo[x_axis].angle = x_position
            # 59 410 44 44, x, y, w, h

            #570 338 51 51
            #print( servo2.kit )
            #servo.q.put(("position",x,y))
            '''


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

                    
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)