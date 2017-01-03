## -------- Generic Communicating Bloc (GCB) --------

__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"


import io
import struct
#import array
import numpy as np
import zmq
#import time
import sys
import time
class GCB_REP_REQ:
    '''
    Here is a generic class Generic Communicating Block (GCB), defined by the following attribute,
        input_ip = [input_ip1,]
        input_port =


    and generating the following methods :
    *** REQ

    *** REP

    '''

    def __init__(self,
        req_ip=[''], ## list of input ip adress to listen
        req_port=[''], ## list of input port to listen, in the same order than req_ip
        rep_port=[''], ## list of output port to write to
        mode_comm='RepReq', ## communication mode. Could a combination of : [(Rep,Push),(Req,Pull)]
        sync=False, ## Put True to the first block to initiate synchronisation signal
        verbose=True):

        self.req_ip=req_ip
        self.req_port=req_port
        self.rep_port=rep_port
        self.verbose=verbose
        self.mode_comm=mode_comm
        self.sync=sync
        self.h = int() ## height, resolution. Value defined in VisionSensor.py
        self.w = int()
        self.timing=list() ## width, resolution. Value defined in VisionSensor.py
        #self._data=[]
        #self.data_to_send=data_to_send

        context = zmq.Context()

        if (self.req_ip != ['']) and (self.req_port != ['']) :
            if 'Req' in self.mode_comm:
                print("Loading Request mode")
                self.socket_req=context.socket(zmq.REQ)
                self._delay_req=list()
                for ip,port in zip(self.req_ip,self.req_port):
                    if self.verbose : print("connecting to tcp://{0}:{1} with REQ method".format(ip,port))
                    self.socket_req.connect("tcp://{0}:{1}".format(ip,port))

            elif 'PushPull' in self.mode_comm:
                print("Loading PushPull mode")
                self.socket_pull=context.socket(zmq.PULL)
                self._delay_pull=list()
                for ip,port in zip(self.req_ip,self.req_port):
                    if self.verbose : print("connecting to tcp://{0}:{1} with PULL method".format(ip,port))
                    self.socket_pull.connect("tcp://{0}:{1}".format(ip,port))

            elif ('Pull' in self.mode_comm and 'Push' not in self.mode_comm):
                print("loading Push mode")
                self.socket_pull = context.socket(zmq.PULL)
                self._delay_pull=list()
                for port in self.rep_port :
                    if self.verbose : print("binding to tcp://*: {0} with Pull method".format(port))
                    self.socket_push.bind("tcp://*:{0}".format(port)) # binding

        if (self.rep_port != ['']) :
            if 'Rep' in self.mode_comm:
                print("Loading response mode")
                self.socket_rep = context.socket(zmq.REP)
                self._delay_rep=list()
                for port in self.rep_port :
                    if self.verbose : print("binding to tcp://*: {0} with REP method".format(port))
                    self.socket_rep.bind("tcp://*:{0}".format(port)) # binding

            elif 'PushPull' in self.mode_comm:
                print("loading PushPull mode")
                self.socket_push = context.socket(zmq.PUSH)
                self._delay_push=list()
                for port in self.rep_port :
                    if self.verbose : print("binding to tcp://*: {0} with REP method".format(port))
                    #self.socket_push.bind("tcp://*:{0}".format(port)) # binding
                    self.socket_push.connect("tcp://localhost:{0}".format(port)) # binding

            elif ('Push' in self.mode_comm and 'Pull' not in self.mode_comm):
                print("loading Push mode")
                self.socket_push = context.socket(zmq.PUSH)
                self._delay_push=list()
                for port in self.rep_port :
                    if self.verbose : print("binding to tcp://*: {0} with PUSH method".format(port))
                    self.socket_push.bind("tcp://*:{0}".format(port)) # binding

        if self.sync==True:
            self.socket_sync=context.socket(zmq.PUSH)
            print(self.req_ip)
            a="tcp://{0}:{1}".format(self.req_ip[0],self.req_port[0])
            print("synchronizing socket initation with : {0}".format(a))
            self.socket_sync.connect("tcp://{0}:{1}".format(self.req_ip[0],self.req_port[0]))

    def REP_array(self,data,flags=0,copy=True,track=False):

        start =time.time()

        ### insert time stamp in data to send to keep track of latency
        print("la taille de data est {0}".format(len(data.shape)))
        if len(data.shape)==2 :
            data1=np.zeros((data.shape[0],data.shape[1],2))
            data1[:,:,0]=data
            data1[0,0,-1]=start
            #print("receiving image in gray scale")

        elif len(data.shape)==3:
            data1=np.zeros((data.shape[0],data.shape[1],data.shape[2]+1))
            data1[:,:,:-1]=data
            data1[0,0,-1]=start
            #print(data1)
            #print("multi_color")

        md = dict(
            dtype = str(data1.dtype),
            shape = data1.shape)
        start=time.time()

        if 'RepReq' in self.mode_comm:
            a=self.socket_rep.recv()
            self.socket_rep.send_json(md, flags|zmq.SNDMORE)
            a_int=self.socket_rep.send(data1, flags, copy=copy, track=track)
            self._delay_rep.append((time.time()-start)*1000)
            #print("le tableau envoyé est de taille : {0}".format(data1.shape))
            #return a_int

        elif 'PushPull' in self.mode_comm:
            #to_send=np.array(([1,2,3],[4,5,6]))
            ##print("avant la transformation : {0}".format(to_send))
            ##print("forme avant l'envoie : {0}".format(to_send.shape))
            #to_send_b=to_send.tobytes()
            ##print("type après transformation : {0}".format(type(to_send_b)))
            a=self.socket_push.send_json(md)
            a_bis=self.socket_push.send(data)
            return a

        elif ('Push' in self.mode_comm and 'Pull' not in self.mode_comm):
            print("on envoie un tableau par la methode push")
            a=self.socket_push.send_json(md)
            a_bis=self.socket_push.send(data)
            return a

    def REQ_array(self, flags=0, copy=True, track=False):
        start=time.time()

        if self.mode_comm=='RepReq':
            self.socket_req.send(b'hello')
            md=self.socket_req.recv_json(flags=flags)
            msg=self.socket_req.recv(flags=flags,copy=copy, track=track)

            self._delay_req.append((time.time()-start)*1000)

            A=np.frombuffer(msg,dtype=md['dtype'])
            A_bis=A.reshape(md['shape'])
            print(A_bis.shape)
            if A_bis.shape[2]==2:
                self._data=A_bis[:,:,0]
                self._data.astype(int)
                timing=A_bis[0,0,1]
            else :
                self._data=A_bis[:,:,:-1]
                self._data.astype(int)
                timing=A_bis[0,0,-1]

            self._data=np.array(self._data,dtype=np.uint8)
            print(self._data.shape)
            self.w=self._data.shape[1]
            self.h=self._data.shape[0]
            timing=round((time.time()-timing)*1000,2)
            self.timing.append(timing)

            if self.verbose==True : self.COM_latency()
            #print(np.max(self._data))
            return self._data

        elif self.mode_comm=='PushPull':
            print("req array with")
            md=self.socket_pull.recv_json(flags=flags)
            msg=self.socket_pull.recv(flags=flags,copy=copy,track=track)
            A=np.frombuffer(msg,dtype=md['dtype'])
            self._data=A.reshape(md['shape'])
            return self._data



    def REQ_array_image(self, flags=0, copy=True, track=False):
        start=time.time()
        if self.mode_comm=='RepReq':
            self.socket_req.send(b'hello')
            md=self.socket_req.recv_json(flags=flags)
            msg=self.socket_req.recv(flags=flags,copy=copy, track=track)
            self._delay_req.append((time.time()-start)*1000)
            A=np.frombuffer(msg,dtype=md['dtype'])

            self._data=A.reshape(md['shape'])

            self.w=self._data.shape[1]
            self.h=self._data.shape[0]
            print("résolution de l'image au niveau de BCG")
            print(self.w,self.h)
            return self._data

        elif self.mode_comm=='PushPull':
            md=self.socket_pull.recv_json(flags=flags)
            msg=self.socket_pull.recv(flags=flags,copy=copy,track=track)
            A=np.frombuffer(msg,dtype=md['dtype'])
            self._data=A.reshape(md['shape'])
            return self._data

    def COM_latency(self): ## Display the communication latency (between sending and receiving)
        if len(self.timing)>4: ### removing the first data to delete bad datas
            average=round(sum(self.timing[3:])/len(self.timing[3:]),2)
            maxi=round(max(self.timing[3:]),2)
            print("--- LAT instant ---  : {0}  ms  --- LAT max ---  : {1} ms  --- LAT avg ---    {2} ms".format(self.timing[-1],maxi,average))

    def display_task_delay(self,list_data):
        if len(list_data)>4:
            average=round(sum(list_data)/len(list_data),2)
            maxi=round(max(list_data),2)
            print("--- TASK instant --- : {0}  ms  --- TASK max --- : {1} ms  --- TASK avg ---   {2} ms".format(list_data[-1],maxi,average))
