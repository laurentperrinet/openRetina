#! /usr/bin/env python3
# -*- coding: utf8 -*-
from __future__ import division, print_function
"""

Base class for the openRetina

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Pierre Albiges, Victor Boutin & Laurent Perrinet INT - CNRS"
import io
import struct
import array
import numpy as np
import zmq
import time
import sys

from multiprocessing.pool import ThreadPool
from collections import deque


class PhotoReceptor:
    """

    Base class for the input to the openRetina

    """
    def __init__(self, w, h, cam_id=0, DOWNSCALE=1, verbose=True):
        self.sleep_time = 2 # let the camera warm up for like 2 seconds
        self.w, self.h = w, h
        #print(w)
        #print(h)
        self.fps = 90
        self.led = False

        #----Which camera handler?----
        try:
            #On Raspbian
            import picamera
            import picamera.array

            self.rpi = True

            self.cap = picamera.PiCamera(cam_id)
            self.cap.start_preview()

            if DOWNSCALE > 1:
                if verbose: print( 'DOWNSCALE NOT IMPLEMENTED YET on the π' )

            self.cap.resolution = (self.w, self.h)
            self.cap.framerate = self.fps
            time.sleep(self.sleep_time)
            self.output = np.empty((self.h, self.w, 3), dtype=np.uint8)
            self.cap.capture(self.output, 'rgb')
            #with picamera.array.PiRGBArray(self.cap) as self.stream:
            #    self.cap.capture(self.stream, format='rgb')

        except ImportError:
            #On other Unix System
            self.rpi = False

            try:
                import cv2
                self.cap = cv2.VideoCapture(cam_id)
                if not self.cap.isOpened(): toto

                print("dim1 : {0}, dim2 : {1}".format(self.h,self.w))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

                self.DOWNSCALE = DOWNSCALE
                if DOWNSCALE > 1:
                    W = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    H = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W/self.DOWNSCALE)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H/self.DOWNSCALE)
                self.h, self.w = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                if verbose: print('Using OpenCV')

            except:
                if verbose: print('Unable to capture video')
    #-------------------------------#

    def grab(self):
        if self.rpi:
            # At this point the image is available as stream.array
            #frame = self.stream.array
            # http://picamera.readthedocs.io/en/latest/recipes2.html?highlight=.array#capturing-to-a-numpy-array
            self.cap.capture(self.output, 'rgb')
        else:
            ret, frame_bgr = self.cap.read()
            self.output = frame_bgr[:, :, ::-1]     #BGR to RGB
        #return frame

    def close(self):
        if self.rpi :
            self.camera.stop_preview()
            self.camera.close()
        else :
            self.cap.release()
            del self.cap

class openRetina(object):
    def __init__(self,
                 model,
                 verb = True,
            ):
        #self.w, self.h = 1920,1080
        #self.w, self.h = 640, 480
        #self.w, self.h = 320, 240
        #self.w, self.h = 1280, 720
        #self.w, self.h = 160, 128
        #self.w, self.h = 1280, 720
        self.w, self.h = 1280, 720 # full resolution for macbook pro
        #self.w, self.h = 160, 128
        # adjust resolution on the rpi
        self.raw_resolution()
        '''
            model is a dict describing the model used
            layer : thalamus,
            input : ['stream','camera','noise']
            output : ['display','capture','stream']
            TSIM : in sec, the duration if the simulation
            ip : ip of the photoreceptor (localhost if on the same machine)
            port : 5566 by default
        '''
        self.model = model
        self.n_cores = 4

        if not 'ip' in self.model.keys(): self.model['ip']='localhost'
        if not 'port' in self.model.keys(): self.model['port']='5566'
        self.verb = verb

        # simulation time
        if not 'T_SIM' in self.model.keys(): self.model['T_SIM'] = 2 # in seconds
        self.refill_time = 0.1 # in seconds

        # displaying options (server side)
        self.do_fs = True
        self.do_fs = False
        self.image_old = np.zeros((self.h, self.w))

        if 'camera' in self.model['input'] :
            self.camera = PhotoReceptor(self.w, self.h)

        if 'stream' in self.model['output'] :
            context = zmq.Context()
            self.socket = context.socket(zmq.REP)
            self.socket.bind("tcp://*:%s" % self.model['port'])
            if self.verb: print("Running retina on port: ", self.model['port'])

    def raw_resolution(self):
        """
        Round a (width, height) tuple up to the nearest multiple of 32 horizontally
        and 16 vertically (as this is what the Pi's camera module does for
        unencoded output).
        """
        self.w = (self.w + 31) // 32 * 32
        self.h = (self.h + 15) // 16 * 16

    def run(self):
        count = 0
        if 'camera' in self.model['input'] : #or  'opencv' in self.model['input'] :
            start = time.time()
            while True:
                # Wait for next request from client
                message = self.socket.recv()
                if self.verb: print("Received request %s" % message)
                if message == b'RIP':
                    finish = time.time()
                    break
                # grab a frame
                self.camera.grab()
                # print("output resolution {0}".format(cam_data.shape))
                # data = self.code(cam_data.reshape((self.h, self.w, 3)))
                # print("output resolution {0}".format(cam_data.shape))
                data = self.code(self.camera.output)
                self.send_array(self.socket, data)
                count += 1
        elif 'noise' in self.model['input'] :
            while True:
                # Wait for next request from client
                message = self.socket.recv()
                if self.verb: print("Received request %s" % message)
                if message == b'RIP':
                    finish = time.time()
                    break
                data = np.random.randint(0, high=255, size=(self.w, self.h, 3))
                # Reset the stream for the next capture
                self.send_array(self.socket, data)
                count += 1

        elif 'stream' in self.model['input'] :
            context = zmq.Context()
            if self.verb: print("Connecting to retina with port %s" % self.model['port'])
            self.socket = context.socket(zmq.REQ)
            self.socket.connect ("tcp://%s:%s" % (self.model['ip'], self.model['port']))

            t0 = time.time()
            start = time.time()
            while time.time()-start < self.model['T_SIM'] + 2*2:
                data = self.request_frame()
                if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
                t0 = time.time()
            self.socket.send (b'RIP')
            self.socket.close()
            # if True:#try:
            #     if 'display' in self.model['output'] :
            #         from openRetina import Canvas
            #         from vispy import app
            #         c = Canvas(self)
            #         app.run()
            #         #disp=other_gui(self)
            #     else:
            #         print('headless mode')
            #         #while time.time()-start < self.model['T_SIM'] + self.sleep_time*2:
            #         while time.time()-start < self.model['T_SIM'] + 2*2:
            #             data = self.request_frame()
            #             if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
            #             t0 = time.time()
            # if True:#finally:
            #     if 'capture' in self.model['output'] :
            #         import imageio
            #         print(self.decode(self.request_frame()).mean())
            #         imageio.imwrite('capture.png', np.fliplr(255*self.decode(self.request_frame())))
            #     self.socket.send (b'RIP')
            #     self.socket.close()
        # print('Sent %d images in %d seconds at %.2ffps' % (
        #         count, finish-start, count / (finish-start)))
        self.socket.close()

    def request_frame(self):
        if self.verb: print("Sending request")
        self.socket.send (b"REQ")
        return self.recv_array(self.socket)

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
        print("Image  ", image.shape, image.min(), image.max())
        return image

    # https://zeromq.github.io/pyzmq/serialization.html
    def send_array(self, socket, A, flags=0, copy=True, track=False):
        """send a numpy array with metadata"""
        md = dict(
            dtype = str(A.dtype),
            shape = A.shape,
        )
        socket.send_json(md, flags|zmq.SNDMORE)
        return socket.send(A, flags, copy=copy, track=track)

    def recv_array(self, socket, flags=0, copy=True, track=False):
        """recv a numpy array"""
        md = socket.recv_json(flags=flags)
        msg = socket.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=md['dtype'])
        return A.reshape(md['shape'])

class other_gui(object):
    def __init__(self, retina):
        self.retina = retina

    def displaying(self):
        while (time.time()-self.start <= self.retina.model['T_SIM']):
            image_to_display = self.retina.request_frame()
            if image_to_diplay is not None:
               cv2.imshow("preview", self.retina.request_frame())
        sys.exit()

try :
    from vispy import app
    from vispy import gloo

    vertex = """
        attribute vec2 position;
        attribute vec2 texcoord;
        varying vec2 v_texcoord;
        void main()
        {
            gl_Position = vec4(position, 0.0, 1.0);
            v_texcoord = texcoord;
        }
    """

    fragment = """
        uniform sampler2D texture;
        varying vec2 v_texcoord;
        void main()
        {
            gl_FragColor = texture2D(texture, v_texcoord);

            // HACK: the image is in BGR instead of RGB.
            float temp = gl_FragColor.r;
            gl_FragColor.r = gl_FragColor.b;
            gl_FragColor.b = temp;
        }
    """

    class Canvas(app.Canvas):
        def __init__(self, retina):
            app.use_app('pyglet')
            self.retina = retina
            app.Canvas.__init__(self, keys='interactive', fullscreen=True, size=(1280, 960))#
            self.program = gloo.Program(vertex, fragment, count=4)
            self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
            self.program['texcoord'] = [(1, 1), (1, 0), (0, 1), (0, 0)]
            self.program['texture'] = np.zeros((self.retina.h, self.retina.w, 3)).astype(np.uint8)
            width, height = self.physical_size
            gloo.set_viewport(0, 0, width, height)
            self._timer = app.Timer('auto', connect=self.on_timer, start=True)
            self.start = time.time()
            self.show()

        def on_resize(self, event):
            width, height = event.physical_size
            gloo.set_viewport(0, 0, width, height)

        def on_draw(self, event):
            gloo.clear('black')
            if time.time()-self.start > self.retina.model['T_SIM']: sys.exit()
            image = self.retina.decode(self.retina.request_frame())
            self.program['texture'][...] = (image*128).astype(np.uint8)
            #self.program['texture'][...]=(data*128).astype(np.uint8)
            self.program.draw('triangle_strip')
        def on_timer(self, event):
            self.update()

except:
    print('💀  Could not load visualisation')
