"""

Base class for the openRetina 


"""
import io
import struct
import numpy as np

class openRetina(object):
    def __init__(self):
        self.ip = '192.168.2.1'
        self.w, self.h = 160, 120
#         self.w, self.h = 320, 240
#         self.w, self.h = 640, 480
        # adjust resolution on the rpi
        self.raw_resolution()
        self.fps = 90

        # simulation time
        self.sleep_time = 2 # let the camera warm up for like 2 seconds
        self.T_SIM = 5 # in seconds

        # displaing options (server side)
        self.display = False
        self.display = True
        self.do_fs = True

    def raw_resolution(self):
        """
        Round a (width, height) tuple up to the nearest multiple of 32 horizontally
        and 16 vertically (as this is what the Pi's camera module does for
        unencoded output).
        """
        self.w = (self.w + 31) // 32 * 32
        self.h = (self.h + 15) // 16 * 16

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
