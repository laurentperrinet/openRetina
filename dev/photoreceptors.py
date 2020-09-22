"""
openRetina : a photoreceptor layer.

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Pierre Albiges, Victor Boutin & Laurent Perrinet INT - CNRS"

from eventRetina import eventRetina
phrs = eventRetina(model=dict(layer='phrs', # label for this layer
                             input=['camera'], # input: can be the camera, noise, a movie (TODO)
                             output=['stream'] # output: can be stream, display, ...
                             ))
phrs.run()
