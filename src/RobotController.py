from threading import Thread
import math
import time
import numpy
import queue


class Stopped(Exception):
    pass


class RobotController(Thread):

    _WHEEL_DIAMETER = 63.75  # mm
    _DISTANCE_BETWEEN_WHEELS = 131  # mm
    _ANGLE_PER_ROTATION = 5.625 / 64
    _STEPS_PER_ROTATION = 4096

    _STEP_SIZE = 32

    _TIME_BETWEEN_STEPS = 1.5  # ms
    _MIN_DISTANCE = 80  # mm

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
            scanDirection = None
            commandIdentifier, value = self.getNextInstruction()
            if commandIdentifier == "move":
                if value > 0:
                    self.setDirectionLF(1, 1)
                    scanDirection = "front"
                else:
                    self.setDirectionLF(-1, -1)
                    scanDirection = "back"
                steps = self.getStepsForCM(abs(value))

            elif commandIdentifier == "turn":
                if value > 0:
                    self.setDirectionLF(-1, 1)
                    # scanDirection = "right"
                else:
                    self.setDirectionLF(1, -1)
                    # canDirection = "left"
                steps = self.getStepsForAngle(abs(value))

            elif commandIdentifier == "stopThread":
                print("MotorControllerThread stopping")
                raise Stopped

            elif commandIdentifier == "scanArray":
                self.scanArray("front", "back", "left", "right")
                continue

            # filling the motorQueue with cycles of steps
            self._motorQueue.clear()
            cycles = [self._STEP_SIZE] * int(steps / self._STEP_SIZE)
            cycles.append(steps % self._STEP_SIZE)  # append rest

            for cycle in cycles:
                self._motorQueue.put_nowait(cycle)

            movedSteps = self.moveAndScan(scanDirection)

            self._saveResult([commandIdentifier, movedSteps])

    def getNextInstruction(self):
        return self._driveInstructions.get()


    def _saveResult(self, result):
        print("Robot: ", result)
        self._results.put(result)

    def getStepsForCM(self, value):
        result = value / (math.pi * self._WHEEL_DIAMETER / self._STEPS_PER_ROTATION)
        return int(result)

    def getStepsForAngle(self, value):
        result = value * (math.pi * self._DISTANCE_BETWEEN_WHEELS / 360) / (math.pi * self._WHEEL_DIAMETER / self._STEPS_PER_ROTATION)
        return int(result)

    def moveAndScan(self, scanDirection):

        def moveScan():
            while not self._motorQueue.empty():
                distance = self._sensors[scanDirection].getData()
                if distance < self._MIN_DISTANCE:
                    self._motorQueue.clear()
                    self._saveResult(["scan", scanDirection, distance])
                    break
                time.sleep(0.25)

        if scanDirection:
            Thread(target=moveScan, name="moveScan").start()
        return self.move()


    def move(self):
        movedSteps = 0
        while not self._motorQueue.empty():
            steps = self._motorQueue.get()
            tLeft = Thread(target=self._moveLeftMotor, name="tLeft", args=(steps, self._TIME_BETWEEN_STEPS))
            tRight = Thread(target=self._moveRightMotor, name="tRight", args=(steps, self._TIME_BETWEEN_STEPS))
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

    def scanArray(self, *scanDirections, returnSensorId=None):

        def measureSensor(scanDirection, resultQueue):
            distance = self._sensors[scanDirection].getData(withTriggerImpuls=False)
            print(scanDirection, distance)
            resultQueue.put([scanDirection, distance])

        resultQueue = queue.Queue()

        for i in range(5):
            threadList = []
            for direction in scanDirections:
                threadList.append(Thread(target=measureSensor,
                                         name=direction,
                                         args=(direction, resultQueue)))
            for thread in threadList:
                thread.start()

            self._sensors["front"].sendTriggerImpuls()

            for thread in threadList:
                thread.join()

        # save entries in a dict to sort them according to sensor source
        # pair of scandirection and distancevalue
        resultDict = {}

        for direction in scanDirections:
            resultDict[direction] = []

        while not resultQueue.empty():
            entry = resultQueue.get()
            if not entry[1] == 0:
                resultDict[entry[0]].append(entry[1])
        print(resultDict)

        # sort out the biggest differences between mean and actual value
        # until a certain treshold of std deviation is unterschritten

        for direction in scanDirections:
            results = resultDict[direction]

            while numpy.array(results).std() > 10:
                arr = numpy.array(results)
                mean = numpy.mean(arr)
                arrMean = abs(arr - mean)
                index = arrMean.tolist().index(arrMean.max())
                del results[index]

            mean = numpy.mean(numpy.array(results))
            resultDict[direction] = mean
            self._saveResult([direction, mean])

        # return the distance value for specific sensor if given
        if returnSensorId:
            return resultDict[returnSensorId][1]
