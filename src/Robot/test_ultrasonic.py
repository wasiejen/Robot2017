from Device import UltraSonicArray4Way
import time
import numpy
from pprint import pprint

array = UltraSonicArray4Way([23, 15, 17, 18], 27)

x = []
ds = []
stddev = []
for pause in range(5):
    # print("\nPAUSENZEIT : ", pause/1000., "\n--------------------------")
    liste = []
    while len(liste) < 4:
        liste.append(array.scanAt("front"))
        if len(liste) > 3:
            if numpy.std(liste) < 20:
                break
            else:
                temp = []
                for el in liste:
                    temp.append(abs(el - sum(liste) / 4))
                del liste[temp.index(max(temp))]
            print(liste)
            if numpy.std(liste) < 20:
                break


    ds.append(sum(liste) / len(liste))
    stddev.append(numpy.std(liste))

for a in zip(ds, stddev):
    print(a)






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

