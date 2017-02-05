from threading import Thread
import math
import time
# import numpy
import queue


class Stopped(Exception):
    pass


class RobotController(Thread):

    _WHEEL_DIAMETER = 63.75  # mm
    _DISTANCE_BETWEEN_WHEELS = 131  # mm
    _ANGLE_PER_ROTATION = 5.625 / 64
    _STEPS_PER_ROTATION = 4096

    _STEP_SIZE = 16

    _TIME_BETWEEN_STEPS = 1.3  # ms
    _MIN_DISTANCE = 150  # mm

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
                self.scanArray(value)
                continue

            # filling the motorQueue with cycles of steps
            self._motorQueue.clear()
            cycles = [self._STEP_SIZE] * int(steps / self._STEP_SIZE)
            cycles.append(steps % self._STEP_SIZE)  # append rest

            for cycle in cycles:
                self._motorQueue.put_nowait(cycle)

            movedSteps = self.moveAndScan(scanDirection)

            self._saveResult([commandIdentifier, movedSteps])
            time.sleep(0.2)

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
                distance = self.scanArray(returnSensorId=scanDirection)
                if distance < self._MIN_DISTANCE:
                    self._motorQueue.clear()
                    self._saveResult([scanDirection, distance])
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


    def scanArray(self, scanDirections="all", returnSensorId=None):

        if scanDirections == "all":
            scanDirections = ["front", "back", "left", "right"]

        def measureSensor(self, scanDirection):
            distance = self._sensors[scanDirection].getData(timeout=0.2,
                                                            withTriggerImpuls=False)
            return (scanDirection, distance)

        resultDict = {}

        for direction in scanDirections:
            resultDict[direction] = []

        threadList = []

        for i in range(5):
            threadList.clear()

            for direction in scanDirections:
                threadList.append(ThreadWithReturn(target=measureSensor,
                                                   name=direction,
                                                   args=(self, direction)))
            for thread in threadList:
                thread.start()
            self._sensors["front"].startTrigger()
            time.sleep(0.00001)
            self._sensors["front"].stopTrigger()
            # self._sensors["front"].sendTriggerImpuls()

            for thread in threadList:
                direction, distance = thread.join()
                if distance <= 0:
                    resultDict[direction].append(100)
                elif distance > 2550:
                    resultDict[direction].append(2550)
                else:
                    resultDict[direction].append(distance)
            time.sleep(0.10)

        # print(resultDict)

        # sort out the biggest differences between mean and actual value
        # until a certain treshold of std deviation is unterschritten

        for direction in scanDirections:
            results = resultDict[direction]

            while pstdev(results) > 30 and len(results) > 2:

                resultMean = mean(results)
                temp = []
                for el in results:
                    temp.append(abs(el - resultMean))
                del results[temp.index(max(temp))]

            resultMean = mean(results)
            resultDict[direction] = resultMean
            self._saveResult([direction, resultMean])

        # return the distance value for specific sensor if given
        if  returnSensorId is not None:
            return resultDict[returnSensorId]

def mean(data):
    """Return the sample arithmetic mean of data."""
    n = len(data)
    if n < 1:
        raise ValueError('mean requires at least one data point')
    return sum(data) / n  # in Python 2 use sum(data)/float(n)

def _ss(data):
    """Return sum of square deviations of sequence data."""
    c = mean(data)
    ss = sum((x - c) ** 2 for x in data)
    return ss

def pstdev(data):
    """Calculates the population standard deviation."""
    n = len(data)
    if n < 2:
        raise ValueError('variance requires at least two data points')
    ss = _ss(data)
    pvar = ss / n  # the population variance
    return pvar ** 0.5


class QueueThread(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.queue = queue.Queue()

    def put(self, item):
        self.queue.put(item)

    def get(self):
        return self.queue.get()

    def empty(self):
        return self.queue.empty()


class ThreadWithReturn(Thread):
    def __init__(self, *args, **kwargs):
        super(ThreadWithReturn, self).__init__(*args, **kwargs)

        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args, **kwargs):
        super(ThreadWithReturn, self).join(*args, **kwargs)

        return self._return

