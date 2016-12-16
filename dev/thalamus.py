# -*- coding: utf8 -*-
from __future__ import division, print_function
"""
openRetina : a photoreceptor layer

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"

import subprocess
p = subprocess.Popen(['/usr/local/bin/ipython3', 'photoreceptors.py'])

from openRetina import openRetina
thalamus = openRetina(model=dict(layer='thalamus',
    input=['stream'], output=['display'],
    T_SIM=120))
thalamus.run()
