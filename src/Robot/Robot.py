# import DeviceStup as Device
import Device as Device
from queue import Queue

import RobotController


class ClearableQueue(Queue):

    def clear(self):
        self.queue.clear()


class Robot(object):

    def __init__(self):

        self.actors = {"mleft": Device.StepperMotor([24, 7, 25, 8], True),
                       "mright": Device.StepperMotor([22, 10, 9, 11], False)}

        self.driveInstructions = ClearableQueue()
        self.motorQueue = ClearableQueue()

        self.sensors = {"front": Device.UltraSonicSensor(23, 27),
                        "right": Device.UltraSonicSensor(15, 27),
                        "left": Device.UltraSonicSensor(17, 27),
                        "back": Device.UltraSonicSensor(18, 27),
                        #"extern": Device.UltraSonicSensor(2, 3),
                        "RaspiLED": Device.RaspiLED()}

        self.results = Queue()

        self.robotController = RobotController.RobotController(self.driveInstructions,
                                                               self.motorQueue,
                                                               self.actors,
                                                               self.sensors,
                                                               self.results)
    #   TODO: Position actualisation -> Aufgabe PC


    def start(self):


        # start = time.time()

        self.robotController.start()

        # for i in range(10):
        # # while time.time() - start < 50:
        #     # print(self.sensors["left"].getData())
        #     # self.driveInstructions.put(["scan", "all"])
        #     self.driveInstructions.put(["scan", ["left", "right", "front", "back"]])
        #
        # # self.driveInstructions.put(["scanArray", ["left"]])
        # # self.driveInstructions.put(["move", 10000])
        # # self.driveInstructions.put(["turn", -90])
        #
        # self.driveInstructions.put(["stopThread", 0])


    def put(self, commandIdentifier, value):
        self.driveInstructions.put([commandIdentifier, value])

    def get(self):
        return self.results.get()

    def clear(self):
        if not self.driveInstructions.empty():
            self.driveInstructions.queue.clear()

    def empty(self):
        return self.results.empty()

    # def move(self, value):
    #     self.driveInstructions.put("move", value)
    #
    # def turn(self, value):
    #     self.driveInstructions.put("turn", value)
    #
    # def scan(self, value):
    #     self.driveInstructions.put("scan", value)

    def stop(self):
        self.clear()
        self.put("stopThread", 0)

    def printResults(self):
        for i in range(self.results.qsize()):
            print(self.results.queue[i])


if __name__ == "__main__":

    robot = Robot()
    robot.start()
