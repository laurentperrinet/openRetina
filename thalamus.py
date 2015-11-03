import zmq
import struct
import numpy as np

from openRetina import openRetina
ret = openRetina()

if ret.stream:
    context = zmq.Context()
    if ret.verb: print("Connecting to retina with port %s" % ret.port)
    ret.socket = context.socket(zmq.REQ)
    ret.socket.connect ("tcp://localhost:%s" % ret.port)

import time
t0 = time.time()
start = time.time()
try:
    if ret.display:
        from openRetina import Canvas
        from vispy import app
        c = Canvas(ret)
        app.run()
    else:
        while time.time()-start < ret.T_SIM + ret.sleep_time*2:
            if ret.verb: print("Sending request")
            ret.socket.send (b"Hello")
            data = ret.recv_array(ret.socket)
            print('Image is ', data.shape, 'FPS=', 1./(time.time()-t0))
            t0 = time.time()

        if ret.capture:
            import imageio
            imageio.imwrite('capture.png', data)

        ret.socket.send (b"RIP")
finally:
#     connection.close()
    ret.socket.close()
