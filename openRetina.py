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

class openRetina(object):
    def __init__(self,
                 verb = True,
            ):
        self.ip = '192.168.2.1'
        self.w, self.h = 1920,1080
        self.w, self.h = 640, 480
        self.w, self.h = 320, 240
        self.w, self.h = 1280, 720
        self.w, self.h = 160, 120
        # adjust resolution on the rpi
        self.raw_resolution()
        self.fps = 90
        self.led = False
        self.n_cores = 4

        self.port = "5566"
        self.verb = verb
        self.stream = True

        # simulation time
        self.sleep_time = 2 # let the camera warm up for like 2 seconds
        self.T_SIM = 5 # in seconds
        self.refill_time = 0.1 # in seconds

        # displaing options (server side)
        self.display = False
        self.display = True
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

    def code(self, stream, connection):
        # Read the image and do some processing on it
        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
#         # "Decode" the image from the array, preserving colour
#         image = cv2.imdecode(data, cv2.CV_LOAD_IMAGE_GRAYSCALE)
# #         image = cv2.cvtColor(image, cv2.cv.CV_BGR2GRAY)
#         r, image = cv2.threshold(image, 127, 255, 1)
         # Construct a numpy array from the stream
#                             data = np.frombuffer(self.stream.getvalue(), dtype=np.uint8).reshape((ret.h, ret.w, 3))
#                             data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
        print('before', data.min(), data.max())
        data = 255 - data
        print(data.min(), data.max())
        stream.seek(0)
        stream.write(array.array('B', data.ravel().tolist()).tostring())
        # write the length of the stream and send it
        connection.write(struct.pack('<L', stream.tell()))
        connection.flush()
        stream.seek(0)
        connection.write(stream.read())

    def decode(self, connection):
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
#             if not image_len:
#                 break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        data = np.fromstring(image_stream.getvalue(), dtype=np.uint8).reshape(self.h, self.w, 3)
        return data

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
        self.retina = retina
        app.Canvas.__init__(self, size=(640, 480), keys='interactive')
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
        if time.time()-self.start < self.retina.T_SIM: # + ret.sleep_time*2: 
            self.retina.socket.send (b"Hello")
        else:
            self.retina.socket.send (b"RIP")
            sys.exit()
#                 data = self.retina.decode(connection)
        data = self.retina.recv_array(self.retina.socket)
        if self.retina.verb: 
            print("Received reply ", data.shape, data.min(), data.max())
        self.program['texture'][...] = data
        self.program.draw('triangle_strip')


    def on_timer(self, event):
        self.update()


if __name__ == '__main__':
    c = Canvas()
    app.run()
    c.cap.release()

