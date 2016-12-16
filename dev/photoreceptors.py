# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : a photoreceptor layer

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

from openRetina import openRetina
phrs = openRetina(model=dict(layer='phrs', input=['opencv'], output=['stream']))
phrs.run()
