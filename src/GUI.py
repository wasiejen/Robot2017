from PyQt5 import QtCore, QtWidgets, uic
import sys
import rpyc

VALUE = 90

# QtWidgets.QMainWindow.setUpdatesEnabled()


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
        self.ui.move_forward.setAutoRepeatInterval(50)
        self.ui.move_forward.setEnabled(False)

        self.ui.move_backwards.clicked.connect(self.move_backwards)
        self.ui.move_backwards.setAutoRepeat(True)
        self.ui.move_backwards.setAutoRepeatInterval(50)
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
        # self.ui.show_scannings.setAutoRepeat(True)
        # self.ui.show_scannings.setAutoRepeatInterval(100)
        self.ui.show_scannings.setEnabled(False)

        # self.ui.camera_prev.clicked.connect(self.cam_preview)
        self.ui.camera_prev.setEnabled(False)

        self.ui.show()

        self.dict_labels = {"move_forward": self.ui.move,
                            "move_backward": self.ui.move,
                            "turn_left": self.ui.turn,
                            "turn_right": self.ui.turn,
                            "moved_forward": self.ui.moved,
                            "moved_backward": self.ui.moved,
                            "turned_left": self.ui.turned,
                            "turned_right": self.ui.turned,
                            "left": self.ui.left,
                            "right": self.ui.right,
                            "front": self.ui.front,
                            "back": self.ui.back,
                            "turn": self.ui.turn,
                            "scanned_at": self.ui.scanned_at,
                            "limit_violated_by": self.ui.violated}

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.set_labels)
        self.flag_scanning = False


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
        # self.ui.camera_prev.setEnabled(True)

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
        self.ui.camera_prev.setEnabled(False)

    def move_forward(self):
        self.robot.put("move_forward", VALUE)

    def move_backwards(self):
        self.robot.put("move_backward", VALUE)

    def turn_left(self):
        self.robot.put("turn_left", VALUE)

    def turn_right(self):
        self.robot.put("turn_right", VALUE)

    def scan(self):
        self.robot.put("scan", "all")

    def clear(self):
        self.robot.clear()

    def cam_preview(self):
        self.robot.test_camera()

    def set_labels(self):
        if not self.robot.empty():
            buffer = self.robot.get()
            if len(buffer) > 10:
                buffer = buffer[-10:0]
            for result in buffer:
                if len(result) > 2:
                    identifier, value = result[2:4]
                else:
                    identifier, value = result
                if type(value) == float:
                    value = int(value)
                self.dict_labels[identifier].setText(str(value))

    def show_scannings(self):
        if self.flag_scanning:
            self.timer.stop()
            self.ui.show_scannings.setText("start scanning")
            self.flag_scanning = False
        else:
            self.timer.start(200)
            self.ui.show_scannings.setText("scanning")
            self.flag_scanning = True


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