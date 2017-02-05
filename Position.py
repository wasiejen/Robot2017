class Position(object):

    def __init__(self, xCoord, yCoord, angle):
        self._xCoord = xCoord
        self._yCoord = yCoord
        self._angle = angle

    def __str__(self):
        return "X: " + str(self._xCoord) + "\t|Y: " + str(self._yCoord) + "\t|Angle: " + str(self._angle)


if __name__ == "__main__":
    test = Position(1, 2, 3)
    print(test)
