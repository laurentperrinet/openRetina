#! /usr/bin/env python3
# -*- coding: utf8 -*-
from __future__ import division, print_function
"""

Base class for the eventRetina

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Pierre Albiges, Victor Boutin & Laurent Perrinet INT - CNRS"

import numpy as np
from openRetina import openRetina

class eventRetina(openRetina):
    def __init__(self, model, verb=True, sparseness=.0001):
        """
        Initializes the eventRetina class which is basically the same as the
        openRetina class but which only transmit a list of events

        """
        openRetina.__init__(self, model, verb=verb)
        self.n_datapoints = int(np.ceil(sparseness*self.h*self.w))
        print('Number of points sent at each frame=', self.n_datapoints)

    def code(self, image):
        image = image.astype(np.float)
        image = image.sum(axis=-1)
        image /= image.std()
        dimage = image - self.image_old
        self.image_old = image

        # see http://blog.invibe.net/posts/2016-11-17-finding-extremal-values-in-a-nd-array.html
        data_ = np.argsort(dimage.ravel())
        # data = np.zeros(self.n_datapoints*2)
        data = np.hstack((data_[:self.n_datapoints], data_[-self.n_datapoints:]))
        return data

    def decode(self, data):
        image = np.zeros((self.h, self.w, 3), dtype=np.int)
        image[:, :, 0][np.unravel_index(data[:self.n_datapoints], (self.h, self.w))] = 1
        image[:, :, -1][np.unravel_index(data[-self.n_datapoints:], (self.h, self.w))] = 1
        # normalize
        print("Image shape: ", image.shape, "Image min: ",image.min(), "Image max:",image.max())
        return image
