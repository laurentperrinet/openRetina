#! /usr/bin/env python3
# -*- coding: utf8 -*-
from __future__ import division, print_function
"""

Base class for the openRetina

See https://github.com/laurentperrinet/openRetina

"""
__author__ = "(c) Pierre Albiges, Victor Boutin & Laurent Perrinet INT - CNRS"
import io
#import struct
#import array
import numpy as np
import zmq
import time
import sys

#from multiprocessing.pool import ThreadPool
#from collections import deque


class PhotoReceptor:
    """

    Base class for the input to the openRetina

    """
    def __init__(self, w, h, cam_id=0, DOWNSCALE=1, verbose=True):
        #self.w, self.h = 1920,1080
        #self.w, self.h = 640, 480
        #self.w, self.h = 320, 240
        #self.w, self.h = 160, 128
        #self.w, self.h = 1280, 720
        #self.w, self.h = 1280, 720 # full resolution for macbook pro
        #self.w, self.h = 128, 72
        #self.w, self.h = 160, 128

        self.sleep_time = .5 # let the camera warm up
        self.w, self.h = w, h
        self.fps = 90
        self.led = False

        #----Which camera handler?----
        try:
            ''' On Raspbian '''
            import picamera
            import picamera.array

            self.rpi = True

            self.cap = picamera.PiCamera(cam_id)
            self.cap.start_preview()

            if DOWNSCALE > 1:
                if verbose: print( 'DOWNSCALE NOT IMPLEMENTED YET on the π' )

            self.cap.resolution = (self.w, self.h)
            # adjust resolution on the rpi
            self.raw_resolution()
            self.cap.framerate = self.fps
            time.sleep(self.sleep_time)
            self.output = np.empty((self.h, self.w, 3), dtype=np.uint8)
            self.cap.capture(self.output, 'rgb')
            #with picamera.array.PiRGBArray(self.cap) as self.stream:
            #    self.cap.capture(self.stream, format='rgb')

        except ImportError:
            ''' On Unix '''
            self.rpi = False
            try:
                import cv2
                self.cap = cv2.VideoCapture(cam_id)
                self.cap.open(0)
                if not self.cap.isOpened():
                    print('Camera is not opened')
                    stop

                self.DOWNSCALE = DOWNSCALE
                print("Before a downscale of {} dim1 : {}, dim2 : {}".format(self.DOWNSCALE, self.h, self.w))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

                if DOWNSCALE > 1:
                    W = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    H = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(W/self.DOWNSCALE))
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(H/self.DOWNSCALE))
                self.h, self.w = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                if verbose: print('Using OpenCV')
                if verbose: print('After a downscale of {}, dim1 : {}, dim2 : {}'.format(self.DOWNSCALE, self.h, self.w))

            except:
                if verbose: print('Unable to capture video')
    #-------------------------------#

    def raw_resolution(self):
        """
        Round a (width, height) tuple up to the nearest multiple of 32 horizontally
        and 16 vertically (as this is what the Pi's camera module does for
        unencoded output).
        """
        self.w = (self.w + 31) // 32 * 32
        self.h = (self.h + 15) // 16 * 16

    def grab(self):
        if self.rpi:
            # At this point the image is available as stream.array
            #frame = self.stream.array
            # http://picamera.readthedocs.io/en/latest/recipes2.html?highlight=.array#capturing-to-a-numpy-array
            self.cap.capture(self.output, 'rgb')
        else:
            ret, frame_bgr = self.cap.read()
            #self.output = frame_bgr[:, :, ::-1]     #BGR to RGB
            frame = frame_bgr
            print('Capture grabbed')
        return frame

    def close(self):
        if self.rpi :
            self.camera.stop_preview()
            self.camera.close()
        else :
            self.cap.release()
            print('Capture released')
            del self.cap

class openRetina(object):
    def __init__(self,
                 model,
                 verb=True,
            ):
        """
        Initializes the openRetina class

        """
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

        if not 'n_cores' in self.model.keys(): self.model['n_cores'] = 1
        if not 'layer' in self.model.keys(): self.model['layer'] = 'openRetina'

        if not 'ip' in self.model.keys(): self.model['ip'] = 'localhost'
        if not 'in_port' in self.model.keys(): self.model['in_port'] = '5566'
        if not 'out_port' in self.model.keys(): self.model['out_port'] = '5566'

        if not 'desired_size' in self.model.keys(): self.model['desired_size'] = (1280, 720)

        self.w, self.h = self.model['desired_size']

        if 'camera' in self.model['input'] :
            self.camera = PhotoReceptor(self.w, self.h)

        self.verb = verb

        # simulation time
        if not 'T_SIM' in self.model.keys(): self.model['T_SIM'] = 2 # in seconds
        self.refill_time = 0.1 # in seconds

        # displaying options (server side)
        self.do_fs = True
        self.do_fs = False

        if 'stream' in self.model['output'] :
            out_context = zmq.Context()
            self.out_socket = out_context.socket(zmq.REP)
            self.out_socket.bind("tcp://*:%s" % self.model['out_port'])
            if self.verb: print("Running out_socket on port: ", self.model['out_port'])


    def run(self):
        count = 0
        if 'camera' in self.model['input'] : #or  'opencv' in self.model['input'] :
            start = time.time()
            while True:
                # checking that in this mode we send data by streaming it out
                assert('stream' in self.model['output'])
                # grab a frame
                self.frame = self.camera.grab()
                # print("output resolution {0}".format(cam_data.shape))
                # data = self.code(cam_data.reshape((self.h, self.w, 3)))
                # print("output resolution {0}".format(cam_data.shape))
                data = self.code(self.frame)
                # Wait for next request from client
                message = self.out_socket.recv()
                if self.verb: print(self.model['layer'], "Camera client received request %s" % message)
                if message == b'RIP':
                    break
                self.send_array(self.out_socket, data)
                count += 1
        elif 'noise' in self.model['input'] :
            while True:
                # Wait for next request from client
                message = self.out_socket.recv()
                if self.verb: print(self.model['layer'], "Noise input received request %s" % message)
                if message == b'RIP':
                    break
                self.frame = np.random.randint(0, high=255, size=(self.w, self.h, 3))
                data = self.code(self.frame)
                # Reset the stream for the next capture
                self.send_array(self.out_socket, data)
                count += 1

        elif 'stream' in self.model['input'] :
            in_context = zmq.Context()
            if self.verb: print(self.model['layer'], "Connecting to retina with port %s" % self.model['in_port'])
            self.in_socket = in_context.socket(zmq.REQ)
            self.in_socket.connect ("tcp://%s:%s" % (self.model['ip'], self.model['in_port']))

            t0 = time.time()
            start = time.time()
            try:
                if 'display' in self.model['output'] :
                    from openRetina import Canvas
                    from vispy import app
                    c = Canvas(self)
                    app.run()
                elif 'stream' in self.model['output'] :
                    while True: #time.time()-start < self.model['T_SIM'] + 2*2:
                        self.frame = self.request_frame()
                        data = self.code(self.frame)
                        # send a message to output port
                        message = self.out_socket.recv()
                        if self.verb: print(self.model['layer'], "Stream input received request %s" % message)
                        if message == b'RIP':
                            break
                        else:
                            # when ready send data
                            self.send_array(self.out_socket, data)
                            count += 1
                else:
                    print('headless mode')
                    #while time.time()-start < self.model['T_SIM'] + self.sleep_time*2:
                    while time.time()-start < self.model['T_SIM'] + 2*2:
                        data = self.request_frame()
                        if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
                        t0 = time.time()
            finally:
                #self.in_socket.send (b'RIP')
                self.in_socket.close()
                if 'capture' in self.model['output'] :
                    import imageio
                    #print("Frame mean: ",self.decode(self.request_frame()).mean())
                    imageio.imwrite('capture.png', np.fliplr(255*self.decode(self.request_frame())))

        finish = time.time()
        print('Sent %d images in %d seconds at %.2ffps' % (
                 count, finish-start, count / (finish-start)))
        if 'stream' in self.model['output'] :
            self.out_socket.close()
        sys.exit()

    def request_frame(self):
        if self.verb: print(self.model['layer'], "is sending request")
        self.in_socket.send (b'REQ')
        return self.recv_array(self.in_socket)

    def code(self, image):
        image = image.astype(np.float)
        image -= image.min()
        image /= (image.max()-image.min())
        return image

    def decode(self, data):
        image = data.copy()
        # normalize
        #print("Image shape: ", image.shape, "Image min: ",image.min(), "Image max:",image.max())
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
            app.Canvas.__init__(self, title=retina.model['layer'],
                                keys='interactive', fullscreen=True, size=(1280, 960))#
            self.program = gloo.Program(vertex, fragment, count=4)
            self.program['position'] = [(-1, -1), (-1, +1), (+1, -1), (+1, +1)]
            self.program['texcoord'] = [(1, 1), (1, 0), (0, 1), (0, 0)]
            self.program['texture'] = np.zeros((self.retina.h, self.retina.w, 3)).astype(np.uint8)
            width, height = self.physical_size
            gloo.set_viewport(0, 0, width, height)
            self._timer = app.Timer('auto', connect=self.on_timer, start=True)
            self.start = time.time()
            self.show()
            self.verb = False

        def on_resize(self, event):
            width, height = event.physical_size
            gloo.set_viewport(0, 0, width, height)

        def on_draw(self, event):
            gloo.clear('black')
            if self.verb: print("Total Duration: ", time.time()-self.start)
            if time.time()-self.start > self.retina.model['T_SIM'] + 2*2:
                self.retina.in_socket.send (b'RIP')
                sys.exit()
            else:
                image = self.retina.decode(self.retina.request_frame())
                self.program['texture'][...] = (image*128).astype(np.uint8)
                self.program.draw('triangle_strip')
                #     if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
        def on_timer(self, event):
            self.update()

except:
    print('💀  Could not load visualisation')
