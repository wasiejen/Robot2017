# import DeviceStup as Device
import Device as Device
from queue import Queue, Empty

import RobotController


class ClearableQueue(Queue):

    def clear(self):
        self.queue.clear()


class Robot(object):

    def __init__(self):

        self.actors = {"motor_left": Device.StepperMotor([24, 7, 25, 8], True),
                       "motor_right": Device.StepperMotor([22, 10, 9, 11], False)}

        self.driveInstructions = ClearableQueue()
        self.motor_queue = ClearableQueue()
        self.scan_queue = ClearableQueue()

        self.sensors = {"front": Device.UltraSonicSensor(23, 27),
                        "right": Device.UltraSonicSensor(15, 27),
                        "left": Device.UltraSonicSensor(17, 27),
                        "back": Device.UltraSonicSensor(18, 27),
                        "RaspiLED": Device.RaspiLED()}

        self.result_queue = Queue()

        self.robot_controller = RobotController.RobotController(self.driveInstructions,
                                                                self.motor_queue,
                                                                self.scan_queue,
                                                                self.actors,
                                                                self.sensors,
                                                                self.result_queue)
        self.robot_controller.daemon = True


    #   TODO: Position actualisation -> Aufgabe PC


    def start(self):
        self.robot_controller.start()

    def put(self, commandIdentifier, value):
        self.driveInstructions.put([commandIdentifier, value])

    def get(self):
        buffer = []
        while True:
            try:
                buffer.append(self.result_queue.get(timeout=0.01))
            except Empty:
                break
        return buffer

    def clear(self):
        self.driveInstructions.queue.clear()
        self.motor_queue.clear()
        self.scan_queue.clear()

    def empty(self):
        return self.result_queue.empty()

    def stop(self):
        self.clear()
        self.put("stopThread", 0)

    def print_results(self):
        for i in range(self.result_queue.qsize()):
            print(self.result_queue.queue[i])


if __name__ == "__main__":

    robot = Robot()
    robot.start()
