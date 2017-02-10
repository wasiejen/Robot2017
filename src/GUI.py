from PyQt5 import QtGui, QtWidgets, uic
import sys
import rpyc
from threading import Thread
import time

VALUE = 4


class RobotGUI(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)

        self.ui = uic.loadUi("firstTestMW.ui")
        self.flag_scanning = None
        self.counter = 0

        self.ui.start_robot.clicked.connect(self.start)

        self.ui.stop_robot.clicked.connect(self.stop)
        self.ui.stop_robot.setEnabled(False)

        self.ui.move_forward.clicked.connect(self.move_forward)
        self.ui.move_forward.setAutoRepeat(True)
        self.ui.move_forward.setAutoRepeatInterval(150)
        self.ui.move_forward.setEnabled(False)

        self.ui.move_backwards.clicked.connect(self.move_backwards)
        self.ui.move_backwards.setAutoRepeat(True)
        self.ui.move_backwards.setAutoRepeatInterval(150)
        self.ui.move_backwards.setEnabled(False)

        self.ui.turn_left.clicked.connect(self.turn_left)
        self.ui.turn_left.setAutoRepeat(True)
        self.ui.turn_left.setAutoRepeatInterval(100)
        self.ui.turn_left.setEnabled(False)

        self.ui.turn_right.clicked.connect(self.turn_right)
        self.ui.turn_right.setAutoRepeat(True)
        self.ui.turn_right.setAutoRepeatInterval(100)
        self.ui.turn_right.setEnabled(False)

        self.ui.scan.clicked.connect(self.scan)
        self.ui.scan.setEnabled(False)

        self.ui.clear_robot.clicked.connect(self.clear)
        self.ui.clear_robot.setEnabled(False)

        self.ui.show_scannings.clicked.connect(self.show_scannings)
        self.ui.show_scannings.setAutoRepeat(True)
        self.ui.show_scannings.setAutoRepeatInterval(100)
        self.ui.show_scannings.setEnabled(False)

        self.ui.show()


    def start(self):
        self.conn = self.conn = rpyc.connect("192.168.178.41", port=1)
        # self.conn = self.conn = rpyc.connect("localhost", port=1)
        self.robot = self.conn.root

        self.ui.start_robot.setEnabled(False)
        self.ui.stop_robot.setEnabled(True)
        self.ui.move_forward.setEnabled(True)
        self.ui.move_backwards.setEnabled(True)
        self.ui.turn_left.setEnabled(True)
        self.ui.turn_right.setEnabled(True)
        self.ui.scan.setEnabled(True)
        self.ui.clear_robot.setEnabled(True)
        self.ui.show_scannings.setEnabled(True)

    def stop(self):

        self.stop_scanning()
        self.conn.close()

        self.ui.start_robot.setEnabled(True)
        self.ui.stop_robot.setEnabled(False)
        self.ui.move_forward.setEnabled(False)
        self.ui.move_backwards.setEnabled(False)
        self.ui.turn_left.setEnabled(False)
        self.ui.turn_right.setEnabled(False)
        self.ui.scan.setEnabled(False)
        self.ui.clear_robot.setEnabled(False)
        self.ui.show_scannings.setEnabled(False)

    def move_forward(self):
        self.robot.put("move", VALUE)

    def move_backwards(self):
        self.robot.put("move", -VALUE)

    def turn_left(self):
        self.robot.put("turn", VALUE)

    def turn_right(self):
        self.robot.put("turn", -VALUE)

    def scan(self):
        self.robot.put("scan", "all")

    def clear(self):
        self.robot.clear()

    def show_scannings(self):


        dictLabels = {"move": self.ui.move,
                      "left": self.ui.left,
                      "right": self.ui.right,
                      "front": self.ui.front,
                      "back": self.ui.back,
                      "turn": self.ui.turn}

        # while not self.robot.empty():
        #     identifier, value = self.robot.get(timeout=0.1)
        #     dictLabels[identifier].setText(str(value))

        def setlabels():

            while self.flag_scanning:
                if not self.robot.empty():
                    identifier, value = self.robot.get()
                    dictLabels[identifier].setText(str(int(value)))
                else:
                    time.sleep(0.05)
        self.stop_scanning()
        self.flag_scanning = True
        Thread(target=setlabels).start()

        self.ui.show_scannings.setText("scanning")

    def stop_scanning(self):
        self.flag_scanning = False
        self.ui.show_scannings.setText("start scanning")
        time.sleep(0.1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    win = RobotGUI()
    sys.exit(app.exec_())


    #
    # def get(self):
    #     return self.results.get()
    #
    #
    # def scan(self, value):
    #     self.driveInstructions.put(["scan", value])