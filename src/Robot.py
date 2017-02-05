import queue
import time

import RobotController

import src.Devices.DeviceStup as Device


class Robot(object):

    def __init__(self):
        self.motorleft = Device.StepperMotor([24, 7, 25, 8], True)
        self.motorright = Device.StepperMotor([22, 10, 9, 11], False)

        self.driveInstructions = queue.Queue()

        self.results = queue.Queue()

        self.motorController = RobotController.RobotController(self.driveInstructions,
                                                               self.motorleft,
                                                               self.motorright,
                                                               self.results)

        self.ultraSonicFront = Device.UltraSonicSensor(27, 23)
        self.ultraSonicRight = Device.UltraSonicSensor(27, 15)
        self.ultraSonicLeft = Device.UltraSonicSensor(27, 17)
        self.ultraSonicBack = Device.UltraSonicSensor(27, 18)

        self.led = Device.RaspiLED()

    #   TODO: THread for USS Array :-D
    #   TODO: Position actualisation


    def start(self):
        self.driveInstructions.put(["move", 100])
        self.driveInstructions.put(["move", -100])
        self.driveInstructions.put(["turn", 90])
        self.driveInstructions.put(["turn", -90])

        self.motorController.start()

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