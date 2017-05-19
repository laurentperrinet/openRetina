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
    def __init__(self,
                 model,
                 verb=True,
            ):
        """
        Initializes the openRetina class

        """
        openRetina.__init__(self, model, verb=verb)

    def code(self, image):#stream, connection):
        #data = image.copy()
        # normalize
#         data -= data.min()
#         data /= data.max()
        data = np.zeros_like(image)
        image = image.astype(np.float)
        image = image.sum(axis=-1)
        image /= image.std()
        dimage = image - self.image_old
        data[:, :, 0] = dimage > dimage.mean() + dimage.std()
        data[:, :, -1] = dimage < dimage.mean() - dimage.std()
        self.image_old = image
        return data

    def decode(self, data):
        image = data.copy()
        # normalize
        print("Image shape: ", image.shape, "Image min: ",image.min(), "Image max:",image.max())
        return image
