from threading import Thread
import math


class Stopped(Exception):
    pass


class RobotController(Thread):

    _diameterWheel = 63.75
    _distanceWheels = 131
    _anglePerStep = 5.625 / 64
    _stepsPerRotation = 4096

    _stepSize = 10

    def __init__(self, driveInstructions, motorleft, motorright, results):
        Thread.__init__(self)
        self._driveInstructions = driveInstructions
        self._motorleft = motorleft
        self._motorright = motorright
        self._results = results

    def run(self):

        while True:
            commandIdentifier, value = self.getNextInstruction()
            if commandIdentifier == "move":
                if value > 0:
                    self.setDirectionLF(1, 1)
                else:
                    self.setDirectionLF(-1, -1)

                steps = self.getStepsForCM(abs(value))

                self.move(steps, waitTime=1.5)

            elif commandIdentifier == "turn":
                if value > 0:
                    self.setDirectionLF(-1, 1)
                else:
                    self.setDirectionLF(1, -1)

                steps = self.getStepsForAngle(abs(value))
                self.move(steps, waitTime=1.5)

            elif commandIdentifier == "stopThread":
                print("MotorControllerThread stopping")
                raise Stopped

            self._results.put([commandIdentifier, value])

    def getNextInstruction(self):
        return self._driveInstructions.get()


    def getStepsForCM(self, value):
        result = value / (math.pi * self._diameterWheel / self._stepsPerRotation)
        return int(result)

    def getStepsForAngle(self, value):
        result = value * (math.pi * self._distanceWheels / 360) / (math.pi * self._diameterWheel / self._stepsPerRotation)
        return int(result)

    def move(self, value, waitTime):
        cycles = [self._stepSize] * int(value / self._stepSize)
        cycles.append(value % self._stepSize) # append rest
        for i in cycles:
            tLeft = Thread(target=self._moveLeftMotor, name="tLeft", args=(i, waitTime))
            tRight = Thread(target=self._moveRightMotor, name="tRight", args=(i, waitTime))
            tLeft.start()
            tRight.start()
            tLeft.join()
            tRight.join()
        self.stop()

    def _moveLeftMotor(self, steps, waittime):
        self._motorleft.moveSteps(steps, waittime)

    def _moveRightMotor(self, steps, waittime):
        self._motorright.moveSteps(steps, waittime)

    def stop(self):
        self._motorleft.stop()
        self._motorright.stop()

    def setDirectionLF(self, left, right):
        self._motorleft.setStepDirection(left)
        self._motorright.setStepDirection(right)
