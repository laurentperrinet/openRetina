OpenRetina
==========

This library contains some utilities to build an event-based retina with open hardware such as a Raspberry Pi along with its camera module, your laptop's webcam or a (test) video.

The goal is to setup an event-based image processing scheme with the following priorities:

- be entirely open-sourced, accessible (in terms of access to the soft- and hard-ware),
- be extensible for use in academics and education,
- mimic key properties of the early visual system in rodents to primates,
- be flexible enough to be multidisciplinary from computer vision to computational neuroscience and from robotics to prosthetics.

The architecture is based on the client (e.g. the Raspberry Pi, your local computer) grasping images and transforming them into events which are then transferred through the network.

Installation
------------

``
	pip3 install git+https://github.com/laurentperrinet/openRetina
``

Do not forget to setup the IP address of your RPi on the network.

Dependencies
-----------

The `openRetina` library needs some dependencies to run:

- ``numpy`` (http://numpy.scipy.org/),
- ``zeromq`` (http://zeromq.org/),
- ``vispy`` is dedicated to the visualization of the `numpy` array,
- You will also need ``IPython`` (http://ipython.scipy.org/) for running interactive sessions
- Some demos require ``matplotlib`` (http://matplotlib.org/) and ``scipy`` (http://www.scipy.org/) as well but this is optional.

On the client, if you use a Raspberry Pi, you should need to only setup ``picamera`` (and its dependencies) and on a local machine, you should need ``opencv`` (to grab images from the webcam) or ``imageio`` to read local video files.

On the π, use:

```
    bash -c "$(curl -fsSL https://raw.githubusercontent.com/laurentperrinet/config-scripts/master/raspbian-setup.sh)"
    sudo apt-get install python3-picamera

```



Example usage
-------------

on your server
``
	python photoreceptors.py
``
on your RaspberryPi:
``
	python retina.py
``

Acknowledgments
----------------

The part of the code for the raspberry client heavily relies on the excellent examples by Dave Jones @ http://picamera.readthedocs.org

To-do
-----

* use http://docs.opencv.org/master/dc/d54/classcv_1_1bioinspired_1_1Retina.html
