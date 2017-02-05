import time

from src import Robot as Robot

if __name__ == "__main__":

    robot = Robot.Robot()
    robot.start()
    time.sleep(5)
    robot.printResults()