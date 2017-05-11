import time
from GCB import GCB_REP_REQ as REP_REQ
import cv2
import numpy as np
import scipy.misc

class DoG(REP_REQ):
    def __init__(self,
                T_SIM='120',
                input_ip=[''],
                input_port=[''],
                mode_comm='RepReq',
                output_port=['']):
        self.input_ip=input_ip
        self.input_port=input_port
        self.output_port=output_port
        self.mode_comm=mode_comm
        self.T_SIM=int(T_SIM)
        REP_REQ.__init__(self,
            req_ip=self.input_ip,
            req_port=self.input_port,
            rep_port=self.output_port,
            mode_comm=self.mode_comm,
            verbose=True)
        self.iterator=0
        print("Resolution dans DoG init {0} {1}".format(self.h,self.w))

    def DoG1_save(self):
        if self.iterator==0:
            self.image_old=np.zeros((self.h,self.w))

        self.output_data = np.zeros((self.h,self.w,3))
        aint=self._data.astype(np.float)
        aint /= self._data.std()
        diff_data= aint - self.image_old
        self.output_data[:, :, 0] = diff_data > diff_data.mean() + diff_data.std()
        #self.output_data[:, :, -1] = diff_data < diff_data.mean() - diff_data.std()
        self.output_data[:, :, -1] = diff_data < diff_data.mean() - diff_data.std()
        #self.output_data[:,:,0]=self.output_data[:, :, 0]* 64/255
        self.output_data=self.output_data.astype(np.uint8)*255
        #print(self.output_data[63,:,0])
        #print(self.output_data[63,:,-1])

        self.image_old=aint
        self.iterator=self.iterator+1
        return self.output_data

    def DoG2(self):
        #Mettre ici le model avec la fonction motion blur
        pass
