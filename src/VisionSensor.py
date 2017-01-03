from GCB import GCB_REP_REQ as REP_REQ
import time
import cv2
import numpy as np
import io

class VisionSensor(REP_REQ):
    def __init__(self,T_SIM='120',
                input_ip =[''],
                input_port = [''],
                output_port=[''],## list of output port to write to
                cam_type="MacOS",
                mode="Gray",
                mode_comm='RepReq',
                divider='2',
                sync=True,
                verbose=True):
        self.input_ip=input_ip
        self.input_port=input_port
        self.output_port=output_port
        self.cam_type=cam_type
        self.T_SIM=int(T_SIM)
        self.divider=int(divider)
        self.mode=mode
        self.verbose=verbose
        self.sync=sync

        REP_REQ.__init__(self,
            req_ip=self.input_ip,    ## list of input ip adress to listen
            req_port=self.input_port,## list of input port to listen, in the same order than req_ip
            rep_port=self.output_port,## list of output port to write to
            mode_comm=mode_comm,  ## communication mode. Could a combination of : [(Rep,Push),(Req,Pull)]
            sync=sync,  ## Put True to the first block to initiate synchronisation signal
            verbose=True)


        if self.cam_type=='MacOS':
            self.cam = cv2.VideoCapture(0)
            self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)/self.divider)
            self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)/self.divider)

            # Remove the first frame, with wrong resolution
            i=0
            while i<2:
                rval,self._data=self.cam.read()
                i=i+1
            self.w=self._data.shape[1]
            self.h=self._data.shape[0]
            if self.verbose : print("la résolution est : {0} * {1}".format(self.h,self.w))

            #print(self._data.shape)

        elif self.cam_type=='PiCam':
            from picamera import PiCamera
            import picamera
            import picamera.array
            self.classe=picamera.array
            self.cam=picamera.PiCamera()
            stream=self.classe.PiRGBArray(self.cam)
            self.h,self.w=self.cam.resolution.height,self.cam.resolution.width
            a=self.cam.capture(stream,format='rgb',use_video_port=True)
            if self.verbose : print("la résolution est : {0} * {1}".format(self.h,self.w))
            '''
            data_int=stream.array
            self.h,self.w = data_int.shape[0],data_int.shape[1]
            print("resolution {0} {1}".format(self.h,self.w))
            teg=self.cam.resolution
            print(type(teg)
            print(teg.width)
            #print(type(data_int.shape))
            #self.cam.resolution = (320, 240)
            '''


    def acquire_frame(self):
        if self.cam_type=='MacOS':
            if self.mode=='Gray':
                rval,data_int=self.cam.read()
                self._data = cv2.cvtColor(data_int, cv2.COLOR_BGR2GRAY)
            else :
                rval,self._data=self.cam.read()
                print(self._data.shape)
            print("aquired shape : {0}".format(self._data.shape))
            return self._data

        elif self.cam_type=='PiCam':
            stream = io.BytesIO()
            for foo in self.cam.capture_continuous(stream, 'bgr', use_video_port=True):
                print(type(stream))
                #print(np.fromstring(dtype=np.uint8))
                stream.seek(0)
                stream.truncate()

                self.code(stream, connection)
                stream.seek(0)
                stream.truncate()
                count += 1
        '''
        elif self.cam_type=='PiCam':
            stream=self.classe.PiRGBArray(self.cam)
            a=self.cam.capture(stream,format='rgb',use_video_port=True)
            data_int=stream.array
            if self.mode=='Gray':
                data_int=cv2.cvtColor(data_int, cv2.COLOR_BGR2GRAY)

            self._data=data_int
            return self._data
        '''
