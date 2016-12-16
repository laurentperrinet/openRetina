# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : a photoreceptor layer

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

import subprocess
### For Raspberry pi
#p = subprocess.Popen(['/usr/bin/python3', 'photoreceptors.py'])
### On Mac OsX
p = subprocess.Popen(['/usr/local/bin/python3', 'photoreceptors.py'])
from openRetina import openRetina
thalamus = openRetina(model=dict(layer='thalamus',
    input=['stream'], output=['display'],
    T_SIM=120))
thalamus.run()
