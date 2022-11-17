#!/usr/bin/python

import time
import numpy as np
from multiprocessing import Process, Queue 
import adafruit_pca9685
from adafruit_servokit import ServoKit


class Servo:
    def __init__(self, queue, pin, kit, verbose="False"):
        self.q = queue
        self.servopin = pin
        self.verbose = verbose
        self.kit = kit
        print("Servo init")

    def start(self):
        self.p = Process(target=self.run, args=((self.q),))
        self.p.start()

    def map(self, value):
        """
        dutycycle value is from 0 to 100,
        value from controller is -1 to 1
        """

        # Y Axis
        if self.servopin == 12: 
            # Don't swap direction
            # Force the value to be 0 and 1
            OldValue = ((value + 1)/2)  # now 0-1
            NewMin = 40
            NewMax = 180
        # X Axis
        else:
             # Swap the direction
            value = value*-1

            # Force the value to be 0 and 1
            OldValue = ((value + 1)/2)  # now 0-1
            NewMin = 0
            NewMax = 180

        # Map to servo specific range
        NewRange = NewMax - NewMin
        NewValue = OldValue * NewRange 
        NewValue = NewValue + NewMin
        return NewValue

    def run(self, queue):
        inp = (0,0,0)

        while True:
            try:
                inp = queue.get_nowait()
                if inp[0] == "position":
                    axis = inp[1]
                    self.dc = self.map(axis)
                    self.kit.servo[self.servopin].angle = self.dc
                    #print("[Servo ",self.servopin,"] Dutycycle changed to ", axis,",", self.dc)
                    #if self.verbose: print("[Servo] Dutycycle changed to ", axis,",", self.dc)
            except:
                time.sleep(0.001)
                pass

if __name__ == "__main__":
    
    print("start servo" + self.servopin)

