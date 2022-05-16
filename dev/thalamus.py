"""
openRetina : a basic thalamic layer.

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Pierre Albiges, Victor Boutin & Laurent Perrinet INT - CNRS"

# import subprocess
# p = subprocess.Popen(['python3 photoreceptors.py'])

from eventRetina import eventRetina
thalamus = eventRetina(model=dict(layer='thalamus', # label for this layer
                             input=['stream'], # input: can be the camera, noise, a movie (TODO)
                             # output=['display'],
                             output=['display','capture'],
                             #output=['capture'], # output: can be stream, display, capture,...
                             T_SIM=20))
thalamus.run()
