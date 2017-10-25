def get_onboard_camera():
    import numpy as np
    import cv2

    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if mirror: 
            img = cv2.flip(img, 1)
        cv2.imshow('vehicle onboard camera', img)
        if cv2.waitKey(1) == 27: 
            break  # esc to quit
    cv2.destroyAllWindows()

get_onboard_camera()