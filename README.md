OpenRetina
==========

This library contains some utilities to build an event-based retina with open hardware such as a Raspberry Pi along with its camera module, your laptop's webcam or a (test) video.

The goal is to setup an event-based image processing scheme with the following priorities:

- be entirely open-sourced, accessible (in terms of access to the soft- and hard-ware),
- be extensible for use in academics and education,
- mimic key properties of the early visual system in rodents to primates.

The architecture is based on the client (e.g. the raspberry pi) grasping images and transforming them into events which are then transferred through the network.

Installation
------------

``
	pip install git+https://meduz.github.com/openRetina
``

Do not forget to setup the IP address of your RPi on the network.

Dependencies
-----------

The opanRetina library needs some dependencies to run:

- numpy (http://numpy.scipy.org/). 
- glumpy is dedicated to numpy visualization, 
- You will also need IPython (http://ipython.scipy.org/) for running interactive sessions
- Some demos require matplotlib (http://matplotlib.sourceforge.net/) and scipy (http://www.scipy.org/) as well but this is optional.

on the client, you should need to only setup picamera (and its dependencies).

Example usage
-------------

on your server
``
	python thalamus.py
``
on your RaspberryPi:
``
	python retina.py
``

Acknowledgements
----------------

The code heavily relies on the excellent exemples by  Dave Jones @ http://picamera.readthedocs.org
