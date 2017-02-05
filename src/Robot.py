from queue import Queue
import time

import RobotController

import src.Devices.DeviceStup as Device


class ClearableQueue(Queue):

    def clear(self):
        self.queue.clear()


class Robot(object):

    def __init__(self):

        self.actors = {"mleft": Device.StepperMotor([24, 7, 25, 8], True),
                       "mright": Device.StepperMotor([22, 10, 9, 11], False)}

        self.driveInstructions = ClearableQueue()
        self.motorQueue = ClearableQueue()

        self.sensors = {"USFront": Device.UltraSonicSensor(27, 23),
                        "USRight": Device.UltraSonicSensor(27, 15),
                        "USLeft": Device.UltraSonicSensor(27, 17),
                        "USBAck": Device.UltraSonicSensor(27, 18),
                        "RaspiLED": Device.RaspiLED()}

        self.results = Queue()

        self.robotController = RobotController.RobotController(self.driveInstructions,
                                                               self.motorQueue,
                                                               self.actors,
                                                               self.sensors,
                                                               self.results)

    #   TODO: THread for USS Array :-D
    #   TODO: Position actualisation


    def start(self):
        self.driveInstructions.put(["move", 100])
        self.driveInstructions.put(["move", -100])
        self.driveInstructions.put(["turn", 90])
        self.driveInstructions.put(["turn", -90])

        self.robotController.start()

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
    time.sleep(5)
    robot.printResults()