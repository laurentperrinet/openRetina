"""

Base class for the openRetina 


"""

class openRetina(object):
    def __init__(self):
        self.ip = '192.168.2.1'
        self.w, self.h = 320, 240
#         self.w, self.h = 640, 480
        # if rpi
        self.raw_resolution()
        self.fps = 30

    def raw_resolution(self):
        """
        Round a (width, height) tuple up to the nearest multiple of 32 horizontally
        and 16 vertically (as this is what the Pi's camera module does for
        unencoded output).
        """
        width, height = resolution
        self.w = (self.w + 31) // 32 * 32
        self.h = (self.h + 15) // 16 * 16


