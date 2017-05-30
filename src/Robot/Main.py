import rpyc
from rpyc.utils.server import ThreadedServer as Server
from Robot import *
import time

_PORT = 1

class Stopped(Exception):
    pass

class ConnectionService(rpyc.Service):
    ALIASES = ["Robot"]

    def on_connect(self):
        self.robot = Robot()
        self.robot.start()
        print("connected")

    def on_disconnect(self):
        self.robot.stop()
        print("disconnected")
        raise Stopped

    def exposed_put(self, commandIdentifier, value):
        self.robot.put(commandIdentifier, value)

    def exposed_get(self):
        return self.robot.get()

    def exposed_empty(self):
        return self.robot.empty()

    def exposed_move(self, value):
        self.robot.move(value)

    def exposed_turn(self, value):
        self.robot.turn(value)

    def exposed_scan(self, value):
        self.robot.scan(value)

    def exposed_clear(self):
        self.robot.clear()

    def exposed_close_server(self):
        raise Stopped

    def exposed_test_camera(self):
        self.robot.camera.test_preview()

if __name__ == '__main__':
    print("Service on Port: ", _PORT, " started.")
    try:
        server = Server(ConnectionService, port=_PORT).start()
    except Exception:
        server.close()
        print("Service stopped.")



