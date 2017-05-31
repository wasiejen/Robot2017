from queue import Queue
from threading import Lock


class Stopped(Exception):
    pass


class ClearableQueue(Queue):

    def clear(self):
        while not self.empty():
            self.get()


class ObjectWithLock(object):

    def __init__(self, value):
        self._value = value
        self._lock = Lock()

    def set(self, value):
        with self._lock:
            self._value = value

    def get(self):
        with self._lock:
            return self._value

    def add(self, value):
        with self._lock:
            self._value += value
            # self._lock.acquire()
            # self._lock.release()