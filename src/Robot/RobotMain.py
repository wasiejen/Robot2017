import rpyc
from rpyc.utils.server import ThreadedServer as Server
from Robot import *

_PORT = 1

class ConnectionService(rpyc.Service):
    ALIASES = ["Robot"]

    def on_connect(self):
        self.robot = Robot()
        self.robot.start()
        print("connected")

    def on_disconnect(self):
        self.robot.stop()
        print("disconnected")


    def exposed_put(self, commandIdentifier, value):
        self.robot.put(commandIdentifier, value)

    def exposed_get(self):
        return self.robot.get()

    def exposed_move(self, value):
        self.robot.put(["move", value])

    def exposed_turn(self, value):
        self.robot.put(["turn", value])

    def exposed_scan(self, value):
        self.robot.put(["scan", value])

if __name__ == '__main__':
    print("Service on Port: ", _PORT, " started.")
    Server(ConnectionService, port=_PORT).start()
    print("Service stopped.")
