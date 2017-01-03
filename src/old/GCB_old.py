## -------- Generic Communicating Bloc (GCB) --------

__author__ = "(c) Victor Boutin & Laurent Perrinet INT - CNRS"


import io
#import struct
#import array
#import numpy as np
import zmq
#import time
import sys

class GCB:
    '''
    Here is a generic class Generic Communicating Block (GCB), defined by the following attribute,
        input_ip = [input_ip1,]
        input_port =


    and generating the following methods :
    *** push

    *** pull

    '''
    def __init__(self,input_ip=[''],input_port=[''],output_port=[''],verbose=True):
        context=zmq.Context()
        if input_ip!=[''] or input_port!=[''] :
            if len(input_ip)==len(input_port) :
                #self.nb_input_port=len(input_ip)
                self.input_ip = input_ip
                self.input_port= input_port
                self.rcv_sockets=list()
                ind0=0
                for i_ip,i_port in zip(self.input_ip,self.input_port):
                    self.rcv_sockets.append(context.socket(zmq.PULL))
                    print("listening  tcp://{0}:{1}".format(i_ip,i_port))
                    #self.receiver.connect("tcp://{0}:{1}".format(i_ip,i_port))
                    self.rcv_sockets[ind0].connect("tcp://localhost:5556")
                    ind0=ind0+1
            else :
                print("WARNING : Not the same number of input ip & input port ")
                raise NameError('SizeMismatch')
        else :
            if verbose : print("No port to listen")

        if output_port!=['']:
        #    self.nb_in
            self.output_port= output_port
            self.binded_port=list()
            ind0=0
            for o_port in self.output_port:
                self.binded_port.append(context.socket(zmq.PUSH))
                print("Ready to bind to port {0}".format(o_port))
                #self.socket.bind("tcp://{0}:{1}".format(o_ip,o_port))
                self.binded_port[ind0].bind("tcp://*:{0}".format(o_port))
                ind0=ind0+1
        else :
            if verbose : print("No port to talk with")

    def pull(self,index=[""]): #Listen the port
        '''
        Receive message on the port selected by the option "index".
        index is a list of the index of input_ip & input_port defined
        at initialization.
        Warning : ip and port in the list input_ip and input_port has
        to be in the same order
        '''
        if index == [""]: ## reception from all port
            ind0=0
            for i_ip,i_port in zip(self.input_ip,self.input_port):
                ## Ici il faudrait mieux stocker les messages dans une listen
                ## ou un dictionnaire
                message = self.rcv_sockets[ind0].recv()
                print(message)
                ind0=ind0+1

        else :
            for ind in index :
                message = self.rcv_sockets[ind].recv()
                print(message)


    def push(self,to_transmit='hello',index=[""]):
        if index == [""]:
            ind0=0
            for o_port in self.output_port:
                self.binded_port[ind0].send(b'this is a test')
                ind0=ind0+1
            print("sent to all {0} port".format(ind0))
        else :
            for ind in index :
                ## transformer en binaire le message to transit, et le faire apparaitre dans le print ce dessus.
                ##self.binded_port[ind].send(ind)
                self.binded_port[ind].send(b'this is another test')
                print("sent to port number {0}".format(ind))
