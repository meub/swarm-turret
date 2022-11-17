#!/usr/bin/env python
import cv2
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        faces = face_cascade.detectMultiScale(image, 1.3, 5)
        array=[0,0,0,0]
        
        #cv2.circle(image, (0,0), 3, (0, 255, 0), -1)#
        #cv2.circle(image, (640,480), 3, (0, 255, 0), -1)

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
            #center_x = x + (w/2)
            #center_y = y + (h/2)
            #cv2.circle(image, (int(center_x), int(center_y)), 3, (0, 255, 0), -1)
            array = [x,y,w,h]
        ret, jpeg = cv2.imencode('.jpg', image)
        return [jpeg.tobytes(),array[0],array[1],array[2],array[3]]