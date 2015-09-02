import io
import socket
import struct
import time
import threading
import picamera
import numpy as np

from openRetina import openRetina
ret = openRetina()

client_socket = socket.socket()
print('This client sends data to IP: ', ret.ip)
client_socket.connect((ret.ip, 8000))
connection = client_socket.makefile('wb')
try:
    connection_lock = threading.Lock()
    pool_lock = threading.Lock()
    pool = []

    class ImageStreamer(threading.Thread):
        def __init__(self):
            super(ImageStreamer, self).__init__()
            self.stream = io.BytesIO()
            self.event = threading.Event()
            self.terminated = False
            self.start()

        def run(self):
            # This method runs in a background thread
            while not self.terminated:
                # Wait for the image to be written to the stream
                if self.event.wait(1):
                    try:
                        with connection_lock:
#                             data = np.frombuffer(self.stream.getvalue(), dtype=np.uint8).reshape((ret.h, ret.w, 3))
                            self.stream.seek(0)
                            # Read the image and do some processing on it
                            # Construct a numpy array from the stream
                            data = np.fromstring(self.stream.getvalue(), dtype=np.uint8)
                                    
                            print(data.min(), data.max())
                            data *= -1
                            data += 256
                            connection.write(struct.pack('<L', self.stream.tell()))
                            connection.flush()
                            self.stream.seek(0)
                            connection.write(self.stream.read())
                    finally:
                        self.stream.seek(0)
                        self.stream.truncate()
                        self.event.clear()
                        with pool_lock:
                            pool.append(self)

    count = 0
    start = time.time()
    finish = time.time()

    def streams():
        global count, finish
        while finish - start < ret.T_SIM:
            with pool_lock:
                if pool:
                    streamer = pool.pop()
                else:
                    streamer = None
            if streamer:
                yield streamer.stream
                streamer.event.set()
                count += 1
            else:
                # When the pool is starved, wait a while for it to refill
                time.sleep(0.1)
            finish = time.time()

    with picamera.PiCamera() as camera:
        pool = [ImageStreamer() for i in range(4)]
        camera.resolution = (ret.w, ret.h)
        camera.framerate = ret.fps
        time.sleep(ret.sleep_time)
        start = time.time()
        camera.capture_sequence(streams(), 'rgb', use_video_port=True)

    # Shut down the streamers in an orderly fashion
    while pool:
        streamer = pool.pop()
        streamer.terminated = True
        streamer.join()

    # Write the terminating 0-length to the connection to let the server
    # know we're done
    with connection_lock:
        connection.write(struct.pack('<L', 0))

finally:
    connection.close()
    client_socket.close()

print('Sent %d images in %d seconds at %.2ffps' % (
    count, finish-start, count / (finish-start)))