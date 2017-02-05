import time

import RobotController

from src import Devices as Device

motorleft = Device.StepperMotor([24, 7, 25, 8], True)
motorright = Device.StepperMotor([22, 10, 9, 11], False)

motorThread = RobotController.RobotController(motorleft, motorright)

ultraSonic1 = Device.UltraSonicSensor(27, 23)
ultraSonic2 = Device.UltraSonicSensor(27, 15)
ultraSonic3 = Device.UltraSonicSensor(27, 17)
ultraSonic4 = Device.UltraSonicSensor(27, 18)
led = Device.RaspiLED()



print(motorleft)
print(motorright)

motorThread.start()

# motorleft.setStepDirection(2)
# motorright.setStepDirection(2)
# motorleft.move(1000,3)
# motorright.move(1000,3)
#
# motorleft.setStepDirection(-2)
# motorright.setStepDirection(-2)
# motorleft.move(1000,3)
# motorright.move(1000,3)

print(ultraSonic1)
print("front: detected Distance in mm: ", ultraSonic1.getdata())
time.sleep(1)
# print(ultraSonic2)
# print("right: detected Distance in mm: ", ultraSonic2.getdata())
# time.sleep(1)
# print(ultraSonic3)
# print("left: detected Distance in mm: ", ultraSonic3.getdata())
# time.sleep(1)
# print(ultraSonic4)
# print("back: detected Distance in mm: ", ultraSonic4.getdata())
# time.sleep(1)


print(led)
# led.blink(10, 0.2)


