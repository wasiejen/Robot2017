# Interface Device and inheriting classes
# Author: Jens Wasielewski
# Date: 16012017

#import RPi.GPIO as GPIO
import time
import random

# Needs to be BCM. GPIO.BOARD lets you address GPIO ports by periperal
# connector pin number, and the LED GPIO isn't on the connector
# GPIO.setmode(GPIO.BCM)
# GPIO.setwarnings(False)


class Device(object):

    def __init__(self, pins):
        raise NotImplementedError("Please Implement this method: __init__")

    def __str__(self):
        raise NotImplementedError("Please Implement this method: __str__")


class ExternalDevice(Device):

    # def setpins(self, pins):
    #     self._pins = pins

    def getpins(self, pins):
        return self._pins

    def _setPinsAsOutput(self):
        for pin in self._pins:
            pass
        #     GPIO.setup(pin, GPIO.OUT)
        # GPIO.output(pin, False)

    def __str__(self):
        return self._name + ": used pins: " + str(self._pins)


class ExternalActor(ExternalDevice):

    def __init__(self, pins):
        self._pins = pins
        self._pincount = len(pins)
        self._setPinsAsOutput()
        self._name = "ExternalActor"


class ExternalSensor(ExternalDevice):

    def __init__(self, pins):
        self._pins = pins
        self._name = "ExternalSensor"

    def getData(self):
        raise NotImplementedError("Please Implement this method: getdata")


class UltraSonicSensor(ExternalSensor):

    def __init__(self, triggerPin, answerPin):
        super().__init__([triggerPin, answerPin])
        self.triggerPin = triggerPin
        self.answerPin = answerPin

        # GPIO.setup(triggerPin, GPIO.OUT)
        # GPIO.setup(answerPin, GPIO.IN)
        #
        # GPIO.output(triggerPin, False)

        self._name = "UltraSonicSensor"

    def getData(self, timeout=1, withTriggerImpuls=True):
        if withTriggerImpuls:
            self.sendTriggerImpuls()
        duration = self.measureTime(timeout)
        distance = self._calculateDistanceInMM(duration)
        return distance

    def sendTriggerImpuls(self):
        # 10 us impuls starts 8 bursts at 40 kHz
        self.startTrigger()
        time.sleep(0.00001)
        self.stopTrigger()

    def startTrigger(self):
        pass

    def stopTrigger(self):
        pass

    def measureTime(self, timeout):

        return 0.1

    def _calculateDistanceInMM(self, duration):
        # speed of sound at sealevel 343000 mm/s
        # distance = duration / 2 * speed
        distance = random.random() * 1000 + 130
        return distance

class Gyroskop(ExternalSensor):

    pass


class StepperMotor(ExternalActor):
    """
    Steppermotor modeltype XXX
    """

    _step_sequence = [[True, False, False, True],
                      [True, False, False, False],
                      [True, True, False, False],
                      [False, True, False, False],
                      [False, True, True, False],
                      [False, False, True, False],
                      [False, False, True, True],
                      [False, False, False, True]]
    _step_sequence_length = len(_step_sequence)
    _stop_sequence = [False, False, False, False]
    _orientationDic = {True: -1, False: 1}


    def __init__(self, pins, isClockwiseForward=True):
        """
        :param pins: with pins connect to to the coils in the motor
        :param isClockwiseForward: rotational direction of the motor, seen from motor to outside
        """
        super().__init__(pins)
        self._name = "StepperMotor"
        self._actualStepNumber = 0
        self._orientation = self._orientationDic[isClockwiseForward];
        self._stepDirection = self._orientation;
        self._stepSize = 1
        self.stop()

    def setStepDirection(self, stepdir=1):
        assert stepdir in [-1, 1]
        self._stepDirection = stepdir * self._orientation

    def getStepDirection(self):
        return self._stepDirection

    def setStepSize(self, stepsize):
        assert stepsize in [1, 2]
        self._stepSize = stepsize

    def getStepSize(self):
        return self._stepSize

    def _setOutputStates(self, sequence):
        # print(sequence)
        for i in range(self._pincount):
            pass
            # GPIO.output(self._pins[i], sequence[i])

    def moveAndStop(self, steps, waitMillisecBetweenSteps):
        self.moveSteps(steps, waitMillisecBetweenSteps)
        self.stop()

    def moveSteps(self, steps, waitMillisecBetweenSteps):
        WaitTime = waitMillisecBetweenSteps / float(1000)

        if self._stepDirection > 0:
            start = self._actualStepNumber + self._stepSize
            end = start + steps
        else:
            start = self._actualStepNumber - self._stepSize
            end = start - steps

        for i in range(start, end, self._stepDirection * self._stepSize):
            self._actualStepNumber = i % self._step_sequence_length
            self._setOutputStates(self._step_sequence[self._actualStepNumber])
            time.sleep(WaitTime)

    def stop(self):
        self._setOutputStates(self._stop_sequence)

    def __str__(self):
        return self._name + ": used pins: " + str(self._pins) + " orientation: " + str(self._orientation)


class InternalDevice(Device):
    pass


class InternalActor(InternalDevice):
    def __init__(self):
        self._name = "InternalActor"

    def __str__(self):
        return self._name


class RaspiSpeaker(InternalActor):

    def __init__(self):
        super().__init__()
        self._name = "RaspiSpeaker"


class RaspiLED(InternalActor):

    def __init__(self):
        super().__init__()
        self._name = "RaspiLED"
        # GPIO.setup(16, GPIO.OUT)

    def blink(self, count, time):
        for i in range(count):
            self.on()
            time.sleep(time*5)
            self.off()
            time.sleep(time)

    def on(self):
        print("led turned on")
        # GPIO.output(16, GPIO.LOW)

    def off(self):
        print("led turned off")
        # GPIO.output(16, GPIO.HIGH)

