from threading import Thread, Event
from HelpClasses import ClearableQueue, ObjectWithLock
import math
import time
import numpy


class RobotController(Thread):

    _WHEEL_DIAMETER = 63.75  # mm
    _DISTANCE_BETWEEN_WHEELS = 131  # mm
    _ANGLE_PER_ROTATION = 5.625 / 64
    _STEPS_PER_ROTATION = 4096

    # _STEP_SIZE = 32
    _STEP_SIZE = 16

    _TIME_BETWEEN_STEPS = 1.1  # ms
    _MIN_DISTANCE = 180  # mm

    _SCAN_TIMEOUT = 0.030

    def __init__(self, drive_instructions, motor_queue, scan_queue, actors, sensors, results):
        Thread.__init__(self)
        self._drive_instructions = drive_instructions
        self._motor_queue = motor_queue
        self._scan_queue = scan_queue
        self._actors = actors
        self._sensors = sensors
        self._motor_left = actors["motor_left"]
        self._motor_right = actors["motor_right"]
        self._results = results

        self._scan_process = Thread(target=self._scan_process_method, name="Scan-Thread")
        self._scan_process.daemon = True
        self._movedStepsCounter = ObjectWithLock(0)

        self.queue_left = ClearableQueue()
        self.queue_right = ClearableQueue()
        self.motor_start_event = Event()
        self.motor_left_rdy = Event()
        self.motor_right_rdy = Event()

        # setup_left = [self._motor_left, self.queue_left, self._TIME_BETWEEN_STEPS, self.motor_start_event, self.motor_left_rdy]
        # setup_right = [self._motor_right, self.queue_right, self._TIME_BETWEEN_STEPS, self.motor_start_event, self.motor_right_rdy]

        self.motor_thread_left = Thread(target=self._moveMotor,
                                        args=(self._motor_left, self.queue_left, self._TIME_BETWEEN_STEPS,
                                              self.motor_start_event, self.motor_left_rdy),
                                        daemon=True)

        self.motor_thread_right = Thread(target=self._moveMotor,
                                         args=(self._motor_right, self.queue_right, self._TIME_BETWEEN_STEPS,
                                               self.motor_start_event, self.motor_right_rdy),
                                         daemon=True)

    def _scan_process_method(self):

        while True:
            scan_directions, limit_directions = self._scan_queue.get()
            scan_directions = self.check_if_all(scan_directions)
            limit_directions = self.check_if_all(limit_directions)
            # assert set(limit_directions).issubset(set(scan_directions))
            self.scan_directions(scan_directions, limit_directions)
            time.sleep(0.1)

    def check_if_all(self, input):
        if input in  ["all", ["all"]]:
            return ["left", "front", "back", "right"]
        else:
            return input

    def scan_directions(self, scan_directions, limit_directions):
        scan_directions = self.check_if_all(scan_directions)
        limit_directions = self.check_if_all(limit_directions)

        result_dict = {}
        for direction in scan_directions:
            result_dict[direction] = self.scan(direction)
            self._save_result(["scanned_at", self._movedStepsCounter.get(), direction, result_dict[direction]])

        limit_violation_list = []
        for direction in limit_directions:
            if result_dict[direction] < self._MIN_DISTANCE:
                limit_violation_list.append(direction)
        if len(limit_violation_list) > 0:
            self._save_result(["limit_violated_by", limit_violation_list])
            self._motor_queue.clear()
            self._drive_instructions.clear()
            return limit_directions

    def scan(self, direction, deviation_limit=0.05):
        result_list = []
        while len(result_list) < 5:
            distance = self._sensors["SonicArray"].scanAt(direction)
            if distance > 3000:
                distance = 3000.
            if distance:
                result_list.append(distance)
            if len(result_list) > 4:
                mean = sum(result_list) / len(result_list)
                if numpy.std(result_list) < (mean * deviation_limit):
                    break
                else:
                    for i in range(2):
                        temp = []
                        for el in result_list:
                            temp.append(abs(el - mean))
                        del result_list[temp.index(max(temp))]
                        mean = sum(result_list) / len(result_list)
                if numpy.std(result_list) < (mean * deviation_limit):
                    break

        return int(sum(result_list) / len(result_list))

    def run(self):
        self.running = True
        self.motor_thread_left.start()
        self.motor_thread_right.start()

        drive_direction_mapping = {"move_forward": (1, 1),
                             "move_backward": (-1, -1),
                             "turn_left": (-1, 1),
                             "turn_right": (1, -1)}

        limit_direction_mapping = {"move_forward": ["front"],
                             "move_backward": ["back"],
                             "turn_left": [],
                             "turn_right": []}

        scan_direction_mapping = {"move_forward": ["front", "left", "right"],
                             "move_backward": ["back", "left", "right"],
                             "turn_left": [],
                             "turn_right": []}

        result_code_mapping = {"move_forward": "moved_forward",
                             "move_backward": "moved_backward",
                             "turn_left": "turned_left",
                             "turn_right": "turned_right"}

        step_mapping = {"move": self.getStepsForMM,
                        "turn": self.getStepsForAngle}

        next_command_identifier, next_value = None, None

        self._scan_process.start()
        self._scan_queue.put(["all", []])
        time.sleep(1)

        while self.running:

            if next_command_identifier is None:
                command_identifier, value = self.getNextInstruction()
            else:
                command_identifier = next_command_identifier
                value = next_value

            if not self._drive_instructions.empty():
                next_command_identifier, next_value = self.getNextInstruction()
            else:
                next_command_identifier, next_value = None, None

            # summing up the values of the same instructions
            while next_command_identifier == command_identifier:
                if type(value) in [int, float]:
                    value += next_value
                    if not self._drive_instructions.empty():
                        next_command_identifier, next_value = self.getNextInstruction()
                    else:
                        # if there is no next command, empty variables for next command
                        next_command_identifier, next_value = None, None
                        break
                else:
                    break

            general_command = command_identifier[0:4]

            if general_command in ["move", "turn"]:
                self._movedStepsCounter.set(0)
                self.setDirectionLF(drive_direction_mapping[command_identifier])
                scan_directions = scan_direction_mapping[command_identifier]
                limit_directions = limit_direction_mapping[command_identifier]
                steps = step_mapping[general_command](value)

                self._save_result([command_identifier, steps])

                # check if no limits are violated, and if continue with next instruction
                violated_limits = self.scan_directions(limit_directions, limit_directions)
                if not violated_limits:
                    self.FillMotorQueue(steps)
                    self.move(scan_directions, limit_directions)
                self._save_result([result_code_mapping[command_identifier], self._movedStepsCounter.get()])

            elif command_identifier == "stopThread":
                print("MotorControllerThread stopping")
                self.running = False

            elif command_identifier == "scan":
                self._scan_queue.put([value, []])


    def getNextInstruction(self):
        return self._drive_instructions.get()

    def FillMotorQueue(self, steps):
        # filling the motorQueue with cycles of steps
        self._motor_queue.clear()
        cycles = [self._STEP_SIZE] * int(steps / self._STEP_SIZE)
        rest = steps % self._STEP_SIZE
        if rest > 0:
            cycles.append(rest)  # append rest

        for cycle in cycles:
            self._motor_queue.put_nowait(cycle)

    def _save_result(self, result):
        print("Robot: ", result)
        self._results.put(result)

    def getStepsForMM(self, value):
        result = value / (math.pi * self._WHEEL_DIAMETER / self._STEPS_PER_ROTATION)
        return int(result)

    def getStepsForAngle(self, value):
        result = value * (math.pi * self._DISTANCE_BETWEEN_WHEELS / 360) / (math.pi * self._WHEEL_DIAMETER / self._STEPS_PER_ROTATION)
        return int(result)

    def move(self, scan_directions=[], limit_directions=[]):
        self._movedStepsCounter.set(0)
        while not self._motor_queue.empty():
            steps = self._motor_queue.get()
            # fill queues for motor threads
            self.queue_left.put(steps)
            self.queue_right.put(steps)
            # signal threads to start
            self.motor_start_event.set()
            # maybe waittime needed before reseting event -> yep it is or else there will be lost steps
            time.sleep(0.001)
            self.motor_start_event.clear()
            # scanning while driving (put between clear and wait to reduce delay)
            if scan_directions != []:
                if self._movedStepsCounter.get() % (15 * self._STEP_SIZE) == 0:
                    self._scan_queue.put([scan_directions, limit_directions])
            # wait for events of motor_threads to be ready to start new round
            self.motor_left_rdy.wait()
            self.motor_right_rdy.wait()
            self._movedStepsCounter.add(steps)
        self.stop()
        self._scan_queue.clear()

    def _moveMotor(self, motor, queue, waittime, start_event, rdy_event):
        while self.running:
            start_event.wait()
            rdy_event.clear()
            steps = queue.get()
            motor.moveSteps(steps, waittime)
            rdy_event.set()

    def stop(self):
        self._motor_left.stop()
        self._motor_right.stop()

    def setDirectionLF(self, dir_tuple):
        left, right = dir_tuple
        self._motor_left.setStepDirection(left)
        self._motor_right.setStepDirection(right)

#
# def mean(data):
#     """Return the sample arithmetic mean of data."""
#     n = len(data)
#     if n < 1:
#         raise ValueError('mean requires at least one data point')
#     return sum(data) / n  # in Python 2 use sum(data)/float(n)
#
# def _ss(data):
#     """Return sum of square deviations of sequence data."""
#     c = mean(data)
#     ss = sum((x - c) ** 2 for x in data)
#     return ss
#
# def pstdev(data):
#     """Calculates the population standard deviation."""
#     n = len(data)
#     if n < 2:
#         raise ValueError('variance requires at least two data points')
#     ss = _ss(data)
#     pvar = ss / n  # the population variance
#     return pvar ** 0.5
#

# class QueueThread(Thread):
#
#     def __init__(self):
#         Thread.__init__(self)
#         self.queue = queue.Queue()
#
#     def put(self, item):
#         self.queue.put(item)
#
#     def get(self):
#         return self.queue.get()
#
#     def empty(self):
#         return self.queue.empty()

#
# class ThreadWithReturn(Thread):
#     def __init__(self, *args, **kwargs):
#         super(ThreadWithReturn, self).__init__(*args, **kwargs)
#
#         self._return = None
#
#     def run(self):
#         if self._target is not None:
#             self._return = self._target(*self._args, **self._kwargs)
#
#     def join(self, *args, **kwargs):
#         super(ThreadWithReturn, self).join(*args, **kwargs)
#
#         return self._return

