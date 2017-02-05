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

    def __init__(self, driveInstructions, motorQueue, actors, sensors, results):
        Thread.__init__(self)
        self._driveInstructions = driveInstructions
        self._motorQueue = motorQueue
        self._actors = actors
        self._sensors = sensors
        self._motorleft = actors["mleft"]
        self._motorright = actors["mright"]
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

            elif commandIdentifier == "turn":
                if value > 0:
                    self.setDirectionLF(-1, 1)
                else:
                    self.setDirectionLF(1, -1)
                steps = self.getStepsForAngle(abs(value))

            elif commandIdentifier == "stopThread":
                print("MotorControllerThread stopping")
                raise Stopped

            # filling the motorQueue with cycles of steps
            self._motorQueue.clear()
            cycles = [self._stepSize] * int(steps / self._stepSize)
            cycles.append(steps % self._stepSize)  # append rest
            for cycle in cycles:
                self._motorQueue.put_nowait(cycle)

            movedSteps = self.move(self._motorQueue, waitTime=1.5)

            self._results.put([commandIdentifier, movedSteps])

    def getNextInstruction(self):
        return self._driveInstructions.get()


    def getStepsForCM(self, value):
        result = value / (math.pi * self._diameterWheel / self._stepsPerRotation)
        return int(result)

    def getStepsForAngle(self, value):
        result = value * (math.pi * self._distanceWheels / 360) / (math.pi * self._diameterWheel / self._stepsPerRotation)
        return int(result)

    def move(self, queue, waitTime):
        movedSteps = 0
        while not queue.empty:
            steps = queue.get()
            tLeft = Thread(target=self._moveLeftMotor, name="tLeft", args=(steps, waitTime))
            tRight = Thread(target=self._moveRightMotor, name="tRight", args=(steps, waitTime))
            tLeft.start()
            tRight.start()
            tLeft.join()
            tRight.join()
            movedSteps += steps
        self.stop()
        return movedSteps

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
