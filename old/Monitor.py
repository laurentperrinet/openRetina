import time
from GCB import GCB_REP_REQ as REP_REQ
import cv2

class monitor(REP_REQ):
    ''' Accessible attibut form REP_REQ class :
        self.socket_req
        self.socket_rep
    '''

    def __init__(self,T_SIM='120',input_ip=[''],input_port=[''],mode_comm='RepReq',verbose=True):
        self.input_ip=input_ip
        self.input_port=input_port
        self.T_SIM=int(T_SIM)
        self.verbose=verbose

        REP_REQ.__init__(self,
                        req_ip=self.input_ip,
                        req_port=self.input_port,
                        rep_port=[''],
                        mode_comm=mode_comm,
                        verbose=True)

    def GUI1_b(self):
        #self._data
        print("data shape dans le gui")
        print(self._data.shape)
        if self._data is not None:
            cv2.imshow("preview",self._data)


    def GUI2(self):
        #Mettre le Gui de Laurent ici
        pass
