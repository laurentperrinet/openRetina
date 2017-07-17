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
    def __init__(self, w, h, cam_id=0, DOWNSCALE=4, verbose=False):
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
        self.verbose = verbose

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

        except:
            ''' On Unix '''
            self.rpi = False
            try:
                import cv2
                self.cap = cv2.VideoCapture(cam_id)
                #self.cap.open(0)
                if not self.cap.isOpened():
                    print('Camera is not opened')
                    stop

                self.DOWNSCALE = DOWNSCALE
                if verbose: print("Before a downscale of {} dim1 : {}, dim2 : {}".format(self.DOWNSCALE, self.h, self.w))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

                if DOWNSCALE > 1:
                    W = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    H = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W//self.DOWNSCALE)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H//self.DOWNSCALE)

                for hack in range(2):
                    frame = self.grab()
                    if verbose: print('Capture grabbed', frame.shape)
                    self.h, self.w, three = frame.shape
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

                #self.h, self.w = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                if verbose: print('Using OpenCV')
                if verbose: print('After a downscale of {}, dim1 : {}, dim2 : {}'.format(self.DOWNSCALE, self.h, self.w))

            except ImportError:
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
            frame = self.cap.capture(self.output, 'rgb')
        else:
            ret, frame_bgr = self.cap.read()
            #self.output = frame_bgr[:, :, ::-1]     #BGR to RGB
            frame = frame_bgr
        if self.verbose: print('Capture grabbed', frame.shape)
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
        if not 'name_capture' in self.model.keys(): self.model['name_capture'] = 'capture.png'

        self.dtype = None
        if 'camera' in self.model['input'] :
            if not 'desired_size' in self.model.keys(): self.model['desired_size'] = (1280, 720)
            self.w, self.h = self.model['desired_size']
            self.camera = PhotoReceptor(self.w, self.h)
            self.w, self.h = self.camera.w, self.camera.h
            self.dtype = None # np.uint8

        if 'noise' in self.model['input'] :
            if not 'desired_size' in self.model.keys(): self.model['desired_size'] = (1280//4, 720//4)
            self.w, self.h = self.model['desired_size']
            self.dtype = None # np.uint8

        self.verb = verb

        # simulation time
        if not 'T_SIM' in self.model.keys(): self.model['T_SIM'] = 2 # in seconds
        self.refill_time = 0.1 # in seconds

        # displaying options (server side)
        self.do_fs = True
        self.do_fs = False


        if 'stream' in self.model['input'] :
            in_context = zmq.Context()
            if self.verb: print(self.model['layer'], "Connecting to retina with port %s" % self.model['in_port'])
            self.in_socket = in_context.socket(zmq.REQ)
            self.in_socket.connect ("tcp://%s:%s" % (self.model['ip'], self.model['in_port']))

        if 'stream' in self.model['output'] :
            out_context = zmq.Context()
            self.out_socket = out_context.socket(zmq.REP)
            self.out_socket.bind("tcp://*:%s" % self.model['out_port'])
            if self.verb: print(self.model['layer'], "Running out_socket on port: ", self.model['out_port'])

        if 'stream' in self.model['input'] :
            if self.verb: print(self.model['layer'], "is asking for the size")
            self.in_socket.send (b'SIZ')
            size =  self.recv_array(self.in_socket)
            self.w, self.h = size[0], size[1]
            if self.verb: print(self.model['layer'], "received the size: (w, h)=", self.w, self.h)

        if 'stream' in self.model['output'] :
            message = b'NIL'
            while not (message == b'SIZ'):
                # Wait for next request from client
                message = self.out_socket.recv()
                if self.verb: print(self.model['layer'], "Camera client received request %s" % message)
            self.send_array(self.out_socket, np.array([self.w, self.h]))

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
                start_dt = time.time()
                message = self.out_socket.recv()
                stop_dt = time.time()
                if self.verb: print(self.model['layer'], "Camera client received request ", message, "waiting ", (stop_dt-start_dt)*1000, "ms")
                if message == b'RIP':
                    #self.capture()
                    break
                start_dt = time.time()
                self.send_array(self.out_socket, data, dtype=self.dtype)
                stop_dt = time.time()
                if self.verb: print(self.model['layer'], "Camera sent data in ", (stop_dt-start_dt)*1000, "ms")
                count += 1
        elif 'noise' in self.model['input'] :
            while True:
                # Wait for next request from client
                message = self.out_socket.recv()
                if self.verb: print(self.model['layer'], "Noise input received request %s" % message)
                if message == b'RIP':
                    self.capture()
                    break
                self.frame = np.random.randint(0, high=255, size=(self.w, self.h, 3))
                data = self.code(self.frame)
                # Reset the stream for the next capture
                self.send_array(self.out_socket, data, dtype=self.dtype)
                count += 1
        elif 'stream' in self.model['input'] :
            t0 = time.time()
            start = time.time()
            if True:#try:
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
                            self.capture()
                            self.in_socket.send (b'RIP')
                            break
                        else:
                            # when ready send data
                            self.send_array(self.out_socket, data, dtype=self.dtype)
                            count += 1
                else:
                    print('headless mode')
                    #while time.time()-start < self.model['T_SIM'] + self.sleep_time*2:
                    while time.time()-start < self.model['T_SIM'] + 2*2:
                        data = self.request_frame()
                        if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
                        t0 = time.time()
            # finally:
            #     self.in_socket.close()


        finish = time.time()
        print(self.model['layer'],  'Sent %d images in %d seconds at %.2ffps' % (
                 count, finish-start, count / (finish-start)))

        if 'stream' in self.model['input'] :
            self.in_socket.close()
        if 'stream' in self.model['output'] :
            self.out_socket.close()
        sys.exit()

    def capture(self):
        print(self.model['layer'],  self.model['output'],  'capture' in self.model['output'])
        if 'capture' in self.model['output']:
            import imageio
            test_frame = self.decode(self.frame)
            if self.verb: print(self.model['layer'],  " capturing a frame ; min-mean-max: ", test_frame.min(), test_frame.mean(), test_frame.max() )
            imageio.imwrite(self.model['name_capture'], np.fliplr(self.frame))

    def request_frame(self):
        if self.verb: print(self.model['layer'], "is asking for a request")
        self.in_socket.send (b'REQ')
        return self.recv_array(self.in_socket, dtype=self.dtype, shape=(self.h, self.w, 3))

    def code(self, image):
        # image = image.astype(np.float)
        # image -= image.min()
        # image /= (image.max()-image.min())
        try:
            return image.astype(np.uint8)
        except:
            return None

    def decode(self, data):
        image = data.copy()
        # normalize
        #print("Image shape: ", image.shape, "Image min: ",image.min(), "Image max:",image.max())
        return image

    # https://zeromq.github.io/pyzmq/serialization.html
    def send_array(self, socket, A, dtype=None, flags=0, copy=True, track=False):
        if dtype is None:
            """send a numpy array with metadata"""
            md = dict(
                dtype = str(A.dtype),
                shape = A.shape,
            )
            socket.send_json(md, flags|zmq.SNDMORE)

        return socket.send(A, flags, copy=copy, track=track)

    def recv_array(self, socket, dtype=None, shape=None, flags=0, copy=True, track=False):
        """recv a numpy array"""
        if dtype is None:
            md = socket.recv_json(flags=flags)
            dtype = md['dtype']
            shape = md['shape']

        msg = socket.recv(flags=flags, copy=copy, track=track)
        A = np.frombuffer(msg, dtype=dtype)
        return A.reshape(shape)

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
            app.Canvas.__init__(self, title=retina.model['title'],
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
                self.retina.capture()
                self.retina.in_socket.send (b'RIP')
                sys.exit()
            else:
                self.retina.frame = self.retina.request_frame()
                image = self.retina.decode(self.retina.frame)
                self.program['texture'][...] = image #(image*255).astype(np.uint8)
                self.program.draw('triangle_strip')
                #     if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
        def on_timer(self, event):
            self.update()

except:
    print('💀  Could not load visualisation')
