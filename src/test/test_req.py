#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#
import struct
import zmq
import time
import numpy as np
import cv2
import timeit

##cv2.namedWindow("preview")

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://10.0.0.1:5555")

def recv_array(socket, flags=0, copy=True, track=False):
    """recv a numpy array"""
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)
    #buf = buffer(msg)
    A = np.frombuffer(msg, dtype=md['dtype'])
    return A.reshape(md['shape'])

i=1
delay_list=list()
delay=0
T_SIM=120
start=time.time()
#  Do 10 requests, waiting each time for a response
while time.time()-start<T_SIM:
    #print("nombre de loop client : {0}".format(i))
    #ping=time.clock()
    #ping=time.time()
    socket.send(b'hola')
    #print("sent client")
    #  Get the reply.
    #flags=0
    #   received_frame = recv_array(socket)
    a=socket.recv()
    print(a)
    #delay=(time.clock()-ping) * 1000## latency in ms
    #delay=(time.time()-ping) * 1000## latency in ms
    #delay_list.append(delay)
    #print("req-rep latency : {0}".format(delay))
    #delay=0
    '''
    ##print("Received reply %s [ %s ]" % (request, message))
    if received_frame is not None:
        cv2.imshow("preview",received_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    '''
    #i=i+1
print("average latency on 100 images : {0}".format(np.mean(delay_list)))
print("maximum latency : {0}".format(max(delay_list)))
print("minimum latency : {0}".format(min(delay_list)))
