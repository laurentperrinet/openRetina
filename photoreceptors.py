import io
import socket
import time
import picamera
from openRetina import openRetina
ret = openRetina()
# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect((ret.ip, 8000))
count = 0
# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
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
finally:
    connection.close()
    client_socket.close()

print('Sent %d images in %d seconds at %.2ffps' % (
    count, finish-start, count / (finish-start)))