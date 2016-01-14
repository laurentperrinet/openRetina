#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Base class for the openRetina 


"""
import io
import struct
import array
import numpy as np
import cv2
import zmq
import time
import sys

from multiprocessing.pool import ThreadPool
from collections import deque

class PhotoReceptor:
    def __init__(self, cam_id=0, DOWNSCALE=1, verbose=True):

        #----Which camera handler?----
        try:
            #On Raspbian
            import picamera
            import picamera.array

            self.rpi = True

            self.camera = picamera.PiCamera(cam_id)
            self.camera.start_preview()

            if DOWNSCALE > 1:
                if verbose: print( 'DOWNSCALE NOT IMPLEMENTED YET on the π' )

            with picamera.array.PiRGBArray(self.camera) as self.stream:
                self.camera.capture(self.stream, format='rgb')

        except:
            #On other Unix System
            self.rpi = False

            try:
                self.cap = cv2.VideoCapture(cam_id)
                if not self.cap.isOpened(): toto

                self.DOWNSCALE = DOWNSCALE
                if DOWNSCALE > 1:
                    W = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                    H = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, W/self.DOWNSCALE)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H/self.DOWNSCALE)
                self.h, self.w = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT), self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

            except:
                if verbose: print('Unable to capture video')
        #-------------------------------#

    def grab(self):
        if self.rpi:
            # At this point the image is available as stream.array
            frame = self.stream.array
        else:
            ret, frame_bgr = self.cap.read()
            frame = frame_bgr[:, :, ::-1]
        return frame

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
        self.model = model
        self.w, self.h = 1920,1080
        self.w, self.h = 640, 480
        self.w, self.h = 320, 240
        self.w, self.h = 1280, 720
        self.w, self.h = 160, 128

        self.image_old = np.zeros((self.h, self.w))

        # adjust resolution on the rpi
        self.raw_resolution()
        self.fps = 90
        self.led = False
        self.n_cores = 4
        
        if not 'ip' in self.model.keys(): self.model['ip']='localhost'
        if not 'port' in self.model.keys(): self.model['port']='5566'
        self.verb = verb

        # simulation time
        self.sleep_time = 2 # let the camera warm up for like 2 seconds
        if not 'T_SIM' in self.model.keys(): self.model['T_SIM'] = 2 # in seconds
        self.refill_time = 0.1 # in seconds

        # displaing options (server side)
        self.do_fs = True
        self.do_fs = False
        self.capture = False
        self.capture = True

    def raw_resolution(self):
        """
        Round a (width, height) tuple up to the nearest multiple of 32 horizontally
        and 16 vertically (as this is what the Pi's camera module does for
        unencoded output).
        """
        self.w = (self.w + 31) // 32 * 32
        self.h = (self.h + 15) // 16 * 16

    def run(self):

        if 'opencv' in self.model['input'] :
            import cv2
            cap = cv2.VideoCapture(0)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)
        elif 'picamera' in self.model['input'] :
            import picamera
            cap = picamera.PiCamera()
            camera.resolution = (self.w, self.h)
            camera.framerate = self.fps
            time.sleep(self.sleep_time)

        if 'stream' in self.model['output'] :
            context = zmq.Context()
            self.socket = context.socket(zmq.REP)
            self.socket.bind("tcp://*:%s" % self.model['port'])
            if self.verb: print("Running retina on port: ", self.model['port'])

        if 'picamera' in self.model['input'] or  'opencv' in self.model['input'] :

            count = 0
            start = time.time()
            if 'picamera' in self.model['input'] :
                stream = io.BytesIO()
                for foo in camera.capture_continuous(stream, 'bgr', use_video_port=True):
                    self.code(stream, connection)
                    # If we've been capturing for more than 30 seconds, quit
                    if message == b'RIP': 
                        finish = time.time()
                        break
                    # Reset the stream for the next capture
                    stream.seek(0)
                    stream.truncate()
                    count += 1
                # Write a length of zero to the stream to signal we're done
                connection.write(struct.pack('<L', 0))
            if 'opencv' in self.model['input'] :
                while True:
                    # Wait for next request from client
                    message = self.socket.recv()
                    if self.verb: print("Received request %s" % message)
                    if message == b'RIP': 
                        finish = time.time()
                        break
                    # grab a frame
                    returned, cam_data = cap.read()
                    data = self.code(cam_data.reshape((self.h, self.w, 3)))
                    # stream it 
                    self.send_array(self.socket, data)
                    count += 1

            if 'noise' in self.model['input'] :
                while True:
                    # Wait for next request from client
                    message = self.socket.recv()
                    if self.verb: print("Received request %s" % message)
                    if message == b'RIP': 
                        finish = time.time()
                        break
                    data = np.random.randint(0, high=128, size=(self.w, self.h, 3))
                    # Reset the stream for the next capture
                    self.send_array(self.socket, data)
                    count += 1
            print('Sent %d images in %d seconds at %.2ffps' % (
                    count, finish-start, count / (finish-start)))
            self.socket.close()

        if 'stream' in self.model['input'] :
            context = zmq.Context()
            if self.verb: print("Connecting to retina with port %s" % self.model['port'])
            self.socket = context.socket(zmq.REQ)
            self.socket.connect ("tcp://%s:%s" % (self.model['ip'], self.model['port']))

            t0 = time.time()
            start = time.time()
            try:
                if 'display' in self.model['output'] :
                    from openRetina import Canvas
                    from vispy import app
                    c = Canvas(self)
                    app.run()
                else:
                    print('headless mode')
                    while time.time()-start < self.model['T_SIM'] + self.sleep_time*2:
                        if self.verb: print("Sending request")
                        self.socket.send (b"Hello")
                        data = self.recv_array(self.socket)
                        if self.verb: print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
                        t0 = time.time()

                    if 'capture' in self.model['output'] :
                        import imageio
                        imageio.imwrite('capture.png', data)
            finally:
                self.socket.send (b"RIP")
                self.socket.close()

    def code(self, image):#stream, connection):
#         data = image.copy()
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
        # Read the image and do some processing on it
#         data = np.fromstring(stream.getvalue(), dtype=np.uint8)
# #         # "Decode" the image from the array, preserving colour
# #         image = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_GRAYSCALE)
# # #         image = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
# #         r, image = cv2.threshold(image, 127, 255, 1)
#          # Construct a numpy array from the stream
# #                             data = np.frombuffer(self.stream.getvalue(), dtype=np.uint8).reshape((ret.h, ret.w, 3))
# #                             data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
#         print('before', data.min(), data.max())
#         data = 255 - data
#         print(data.min(), data.max())
#         stream.seek(0)
#         stream.write(array.array('B', data.ravel().tolist()).tostring())
#         # write the length of the stream and send it
#         connection.write(struct.pack('<L', stream.tell()))
#         connection.flush()
#         stream.seek(0)
#         connection.write(stream.read())

    def decode(self, data):
        image = data.copy()
        # normalize
        print("Image  ", image.shape, image.min(), image.max())
        
        return image
#         
#         # Read the length of the image as a 32-bit unsigned int. If the
#         # length is zero, quit the loop
#         image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
# #             if not image_len:
# #                 break
#         # Construct a stream to hold the image data and read the image
#         # data from the connection
#         image_stream = io.BytesIO()
#         image_stream.write(connection.read(image_len))
#         # Rewind the stream, open it as an image with PIL and do some
#         # processing on it
#         image_stream.seek(0)
#         data = np.fromstring(image_stream.getvalue(), dtype=np.uint8).reshape(self.h, self.w, 3)
#         return data

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
#         buf = buffer(msg)
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
                if self.retina.verb: print("Sending request")
                if time.time()-self.start < self.retina.model['T_SIM']: # + ret.sleep_time*2: 
                    self.retina.socket.send (b"Hello")
                else:
                    sys.exit()
                data = self.retina.recv_array(self.retina.socket)
                if self.retina.verb: 
                    print("Received reply ", data.shape, data.min(), data.max())
                image = self.retina.decode(data)
                self.program['texture'][...] = (image*128).astype(np.uint8)
                self.program.draw('triangle_strip')


            def on_timer(self, event):
                self.update()


        if __name__ == '__main__':
            c = Canvas()
            app.run()
            c.cap.release()
    except :
        pass
