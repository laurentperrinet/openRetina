#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
import struct
import time
import zmq
import cv2
import numpy as np
import timeit



context = zmq.Context()
socket = context.socket(zmq.REP) ## écoute sur
socket.bind("tcp://*:5555") ## bind pour écouter

#cv2.namedWindow("preview")
#cap = cv2.VideoCapture(0)
#rval,frame=cap.read()

#h, w = cap.get(cv2.CAP_PROP_FRAME_HEIGHT), cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#print("resolution : {0} * {1}".format(h,w))
#if not cap.isOpened():
#    print("Cannot open the camera")

i=1

def send_array(socket, A, flags=0, copy=True, track=False):
    """send a numpy array with metadata"""
    md = dict(
        dtype = str(A.dtype),
        shape = A.shape,
    )
    socket.send_json(md, flags|zmq.SNDMORE)
    #delay_processing=(time.clock()-top2)*1000
    #list_delay_processing.append(delay_processing)
    #delay_processing=0
    return socket.send(A, flags, copy=copy, track=track)
i=0
list_delay_request=list()
list_delay_processing=list()
delay=0
while i<1000:

    '''
    if frame is not None:
        cv2.imshow("preview",frame)
    '''
    #  Wait for next request from client

    print("nb de loop serveur: {0}".format(i))
    pingb=socket.recv()
    print(pingb)
    #ping=struct.unpack('f',pingb)
    ##delay = (time.clock()-ping[0])
    #print(delay)
    ##list_delay_request.append(delay)
    #delay=0


    #top2=time.clock()

    #print("Received server")

    #  Do some 'work'
    #ret, frame = cap.read()
    #print("size of the frame : {0}".format(frame.nbytes))
    ## sending frame to client
    #send_array(socket, frame)
    #print("sent server")
    a=socket.send(b'hello')

    i=i+1

#print("average latency to receive a request : {0}".format(np.mean(list_delay_request)))
#print("average latency for processing : {0}".format(np.mean(list_delay_processing)))
    #  Send reply back to client
