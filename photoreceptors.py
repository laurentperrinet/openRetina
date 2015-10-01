import numpy as np
import zmq
import time
try:
    import picamera
    rpi = True
except:
    print('no rpi')
    rpi = False
from openRetina import openRetina
ret = openRetina()

if ret.stream:
    context = zmq.Context()
    ret.socket = context.socket(zmq.REP)
    ret.socket.bind("tcp://*:%s" % ret.port)
    if ret.verb: print("Running server on port: ", ret.port)

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
# client_socket = socket.socket()
# client_socket.connect((ret.ip, 8000))
count = 0
# # Make a file-like object out of the connection
# connection = client_socket.makefile('wb')
try:
    if rpi:
        with picamera.PiCamera() as camera:
            camera.resolution = (ret.w, ret.h)
            camera.framerate = ret.fps
            time.sleep(ret.sleep_time)
            # Note the start time and construct a stream to hold image data
            # temporarily (we could write it directly to connection but in this
            # case we want to find out the size of each capture first to keep
            # our protocol simple)
            start = time.time()
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'bgr', use_video_port=True):
                ret.code(stream, connection)
                # If we've been capturing for more than 30 seconds, quit
                if time.time() - start > ret.T_SIM:
                    finish = time.time()
                    break
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
                count += 1
        # Write a length of zero to the stream to signal we're done
        connection.write(struct.pack('<L', 0))

    else:
        start = time.time()
        while True:
            print('waiting')
            # Wait for next request from client
            message = ret.socket.recv()
            if ret.verb: print("Received request %s" % message)

            if time.time() - start > ret.T_SIM:
                finish = time.time()
                break
            data = np.random.randint(0, high=128, size=(ret.w, ret.h, 3))
            # Reset the stream for the next capture
            ret.send_array(ret.socket, data)
            count += 1
finally:
    ret.socket.close()

print('Sent %d images in %d seconds at %.2ffps' % (
    count, finish-start, count / (finish-start)))