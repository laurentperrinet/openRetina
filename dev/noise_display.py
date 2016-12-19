# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : testing the output Canvas with noise

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

from openRetina import openRetina


import threading
import time

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, input, output):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.node = openRetina(model=dict(layer=name, # label for this layer
                                     input=input, # input: can be the camera, noise, a movie (TODO)
                                     output=output, # output: can be stream, display, ...
                                     T_SIM=120))
    def run(self):
        print ("Starting " + self.name)
        self.node.run()
        print ("Exiting " + self.name)

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

# Create new threads
thread1 = myThread(1, 'test_noise', input=['noise'], output=['stream'])
# thread2 = myThread(2, 'test_display', # label for this layer
#                              input=['stream'], # input: can be the camera, noise, a movie (TODO)
#                              output=['display'], # output: can be stream, display, capture,...
#                              )

# Start new Threads
thread1.start()
#thread2.start()

thalamus = openRetina(model=dict(layer='test_display', # label for this layer
                             input=['stream'], # input: can be the camera, noise, a movie (TODO)
                             output=['display'], # output: can be stream, display, capture,...
                             T_SIM=120))

thalamus.run()

thread1.join()
#thread2.join()

print ("Exiting Main Thread")

#
# import multiprocessing
# phrs = openRetina(model=dict(layer='test_noise', # label for this layer
#                              input=['noise'], # input: can be the camera, noise, a movie (TODO)
#                              output=['stream'] # output: can be stream, display, ...
#                              ))
#
# thread_noise = multiprocessing.Process(target=phrs.run)
# thread_noise.start()
#
#
#
# thalamus = openRetina(model=dict(layer='test_display', # label for this layer
#                              input=['stream'], # input: can be the camera, noise, a movie (TODO)
#                              output=['display'], # output: can be stream, display, capture,...
#                              T_SIM=120))
#
# #thalamus.run()
# thread_display = multiprocessing.Process(target=thalamus)
# thread_display.start()
