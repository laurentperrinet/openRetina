#! /usr/bin/env python3
# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : a photoreceptor layer

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

from openRetina import openRetina
phrs = openRetina(model=dict(layer='phrs', # label for this layer
                             input=['camera'], # input: can be the camera, noise, a movie (TODO)
                             output=['stream'] # output: can be stream, display, ...
                             ))
phrs.run()
