# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : testing the output Canvas with noise

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

from openRetina import openRetina

import multiprocessing
phrs = openRetina(model=dict(layer='test_noise', # label for this layer
                             input=['noise'], # input: can be the camera, noise, a movie (TODO)
                             output=['stream'] # output: can be stream, display, ...
                             ))

thread_noise = multiprocessing.Process(target=phrs.run)
thread_noise.start()



thalamus = openRetina(model=dict(layer='test_display', # label for this layer
                             input=['stream'], # input: can be the camera, noise, a movie (TODO)
                             output=['display'], # output: can be stream, display, capture,...
                             T_SIM=120))

#thalamus.run()
thread_display = multiprocessing.Process(target=thalamus)
thread_display.start()
