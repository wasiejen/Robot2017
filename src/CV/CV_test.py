import rpyc
from rpyc.utils.server import ThreadedServer as Server

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import copy
import pickle
# import cv2

# # initialize the camera and grab a reference to the raw camera capture

#
# # grab an image from the camera
# camera.capture(rawCapture, format="bgr")
# image = rawCapture.array
#
# # display the image on screen and wait for a keypress
# cv2.imshow("Image", image)
# cv2.waitKey(0)


class Service(rpyc.Service):

    def on_connect(self):
        print("connection established")
        # self._conn._config.update(dict(allow_pickle = True))

        self.camera = PiCamera()
        self.exposed_camera = self.camera
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32

        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        #self.camera.capture(self.rawCapture, format="bgr")
        # allow the camera to warmup
        time.sleep(0.1)



    def on_disconnect(self):
        print("connection closed")
        self.camera.close()

    def exposed_get(self):
        self.camera.capture(self.rawCapture, format="bgr")
        return copy.deepcopy(self.rawCapture.array)

    def exposed_getgen(self):
        for frame in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            yield frame.array
            self.rawCapture.truncate(0)

if __name__ == '__main__':

    _PORT = 1
    print("Service on Port: ", _PORT, " started.")
    try:
        server = Server(Service, port=_PORT, protocol_config={"allow_pickle": True}).start()
    except Exception:
        server.close()
        print("Service stopped.")