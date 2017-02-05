# import Devices.DeviceStup as Device
import Devices.Device as Device
from queue import Queue
import time

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

        self.sensors = {"front": Device.UltraSonicSensor(27, 23),
                        "right": Device.UltraSonicSensor(27, 15),
                        "left": Device.UltraSonicSensor(27, 17),
                        "back": Device.UltraSonicSensor(27, 18),
                        "RaspiLED": Device.RaspiLED()}

        self.results = Queue()

        self.robotController = RobotController.RobotController(self.driveInstructions,
                                                               self.motorQueue,
                                                               self.actors,
                                                               self.sensors,
                                                               self.results)
    #   TODO: Position actualisation


    def start(self):
        self.driveInstructions.put(["scanArray", "all"])
        self.driveInstructions.put(["scanArray", "all"])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])
        self.driveInstructions.put(["move", 10000])
        self.driveInstructions.put(["turn", -90])

        self.driveInstructions.put(["turn", -90])

        self.driveInstructions.put(["stopThread", 0])

        self.robotController.start()
        # self.robotController.scanArray("front")
        # time.sleep(5)
        # self.robotController.scanArray("back")

    def put(self, commandIdentifier, value):
        self.driveInstructions.put([commandIdentifier, value])

    def clear(self):
        self.driveInstructions.queue.clear()

    def move(self, value):
        self.driveInstructions.put(["move", value])

    def turn(self, value):
        self.driveInstructions.put(["turn", value])

    def stopThread(self):
        self.clear()
        self.put("stopThread", 0)

    def printResults(self):
        for i in range(self.results.qsize()):
            print(self.results.queue[i])


if __name__ == "__main__":

    robot = Robot()
    robot.start()

    # start = time.time()
    # while time.time() - start < 50:
    #     print(robot.sensors["front"].getData())
    #     time.sleep(0.25)
    #
    # start = time.time()
    # while time.time() - start < 50:
    #     print(robot.sensors["back"].getData())
    #     time.sleep(0.25)
    #
    # start = time.time()
    # while time.time() - start < 50:
    #     print(robot.sensors["left"].getData())
    #     time.sleep(0.25)
    #
    # start = time.time()
    # while time.time() - start < 50:
    #     print(robot.sensors["right"].getData())
    #     time.sleep(0.25)



    # time.sleep(5)
    # robot.printResults()