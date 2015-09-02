import io
import socket
import struct
import time
import picamera
w, h = 640, 480
w, h = 200, 100
w, h = 320, 240
# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
client_socket = socket.socket()
client_socket.connect(('192.168.0.4', 8000))
client_socket.connect(('192.168.2.1', 8000))

def raw_resolution(resolution):
    """
    Round a (width, height) tuple up to the nearest multiple of 32 horizontally
    and 16 vertically (as this is what the Pi's camera module does for
    unencoded output).
    """
    width, height = resolution
    fwidth = (width + 31) // 32 * 32
    fheight = (height + 15) // 16 * 16
    return fwidth, fheight


def bytes_to_rgb(data, resolution):
    """
    Converts a bytes objects containing RGB/BGR data to a `numpy`_ array.
    """
    width, height = resolution
    fwidth, fheight = raw_resolution(resolution)
    if len(data) != (fwidth * fheight * 3):
        raise PiCameraValueError(
            'Incorrect buffer length for resolution %dx%d' % (width, height))
    # Crop to the actual resolution
    return np.frombuffer(data, dtype=np.uint8).\
            reshape((fheight, fwidth, 3))[:height, :width, :]

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (w, h)
        camera.framerate = 30
        # Start a preview and let the camera warm up for 2 seconds
        camera.start_preview()
        time.sleep(2)

        # Note the start time and construct a stream to hold image data
        # temporarily (we could write it directly to connection but in this
        # case we want to find out the size of each capture first to keep
        # our protocol simple)
        start = time.time()
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'bgr', use_video_port=True):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            # Rewind the stream and send the image data over the wire
            stream.seek(0)
            connection.write(stream.read())
            # If we've been capturing for more than 30 seconds, quit
            if time.time() - start > 30:
                break
            # Reset the stream for the next capture
            stream.seek(0)
            stream.truncate()
    # Write a length of zero to the stream to signal we're done
    connection.write(struct.pack('<L', 0))
finally:
    connection.close()
    client_socket.close()