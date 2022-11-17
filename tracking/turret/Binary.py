#!/usr/bin/python

import time
import numpy as np
from multiprocessing import Process, Queue 

class Binary:
    def __init__(self, queue, pin, kit, axis="A", verbose="False"):
        self.q = queue
        self.pin = pin
        self.kit = kit
        self.state = 0
        self.debounce_time = 0.2
        self.last_button_ts = 0
        self.axis=axis
        self.verbose = verbose

    def start(self):
        self.p = Process(target=self.run, args=((self.q),(self.kit),))
        self.p.start()

    def run(self, queue, kit):
        inp = (0,0,0)

        while True:
            try:
                inp = queue.get_nowait()
                if self.verbose: print(inp)
                if inp[0] == self.axis and time.time() - self.last_button_ts > self.debounce_time:
                    print("[Button] Pressed for pin: ", self.pin)

                    try:
                        # Start the firing process
                        kit.servo[self.pin].angle = 100
                        time.sleep(0.3)
                        # Set back to zero
                        kit.servo[self.pin].angle = 0
                    except Exception as e:
                        print("Could not fire")
                        print( e )
                
                self.last_button_ts = time.time()
            except:
                time.sleep(0.01)
                pass

if __name__ == "__main__":

    print("Start binary")
