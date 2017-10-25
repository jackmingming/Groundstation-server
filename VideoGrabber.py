import cv2
import numpy as np


"""
Examples of objects for image frame aquisition from both IP and
physically connected cameras
Requires:
 - opencv (cv2 bindings)
 - numpy
"""

class Camera(object):

    def __init__(self, camera=0):
        self.cam = cv2.VideoCapture(camera)
        if not self.cam:
            raise Exception("Camera not accessible")

    def get_frame(self):
        while True:
            ret_val, img = self.cam.read()
            img = cv2.flip(img, 1)
            cv2.imshow('my webcam', img)
            if cv2.waitKey(1) == 27: 
                break  # esc to quit
        cv2.destroyAllWindows() 