import rpyc
import cv2
import numpy
from copy import deepcopy
import matplotlib.pyplot as plt

conn = rpyc.connect("192.168.178.41", port=1)#, config={"allow_pickle": True})

# img_netref = conn.root.get()
# cv2.imshow("image",  deepcopy(img_netref))
# cv2.waitKey(0)


frames = conn.root.getgen()

while True:
    frame = rpyc.utils.classic.obtain(next(frames))
    # frame = deepcopy(next(frames))
    cv2.imshow("video", frame)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break



#
# camera = conn.root.camera
# # camera.resolution = (1920, 1080)
# plt.imshow(image)
# plt.show()