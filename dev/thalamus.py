# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : a photoreceptor layer

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

import subprocess
p = subprocess.Popen(['./photoreceptors.py'])
from openRetina import openRetina
thalamus = openRetina(model=dict(layer='thalamus', # label for this layer
                             input=['stream'], # input: can be the camera, noise, a movie (TODO)
                             output=['display', 'capture'], # output: can be stream, display, capture,...
                             T_SIM=120))
thalamus.run()
