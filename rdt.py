import random
from socket import *
import threading
import time

class RDTSender:

    def __init__(self,socket):
        self.socket=socket
        self.states={}#dictionary of active connection states



    def handshake(self):
        id=str(time.time())
        formatted_msg='HANDSHAKE '+id
        self.socket.sendto(formatted_msg.encode,addr)
        self.socket.recvfrom(2048)
        self.states[id]=0

    def rdt_send(self, bytes,addr):
        id=str(addr)
        if id not in self.states:
            self.states[id]=0
            print("Sender: new id "+id)
        if self.states[id]==0:
            self.udt_send(bytes,0,addr)
            self.waitACK(0,id)
            self.states[id]=1
            print("Sender: State is now 1")
        elif self.states[id]==1:
            self.udt_send(bytes,1,addr)
            self.waitACK(1,id)
            self.states[id]=0
            print("Sender: State is now 0")

    def waitACK(self,ack_number,prev_id):
        print("Sender "+prev_id+" waiting for ack " +str(ack_number))
        while True:
            bytes,addr=self.socket.recvfrom(2048)
            ack_num = int(bytes[0:1]) # Extract the sequence number from the message
            id=str(addr)
            if id == prev_id and self.isACK(bytes) and ack_num==ack_number:
                print("Sender: Ack "+str(ack_number)+" Received")
                return


    def udt_send(self,bytes,seqnum,addr):
        seq_byte=str(seqnum).encode()
        data=b''.join([seq_byte,bytes])
        print("Sender: sending "+data.decode())
        self.socket.sendto(data,addr)


    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, ack):
        if len(ack) == 1:
            return True
        else:
            return False

class RDTReceiver:
    def __init__(self,socket):
        self.states={} #dictionary of active connection states
        self.socket=socket
    def rdt_recv(self,bufsize):
        while True:
            bytes,addr=self.socket.recvfrom(bufsize)   # Receive the UDP packet
            print("Receiver: received "+bytes.decode())
            id=str(addr)
            seq = int(bytes[0:1]) # Extract the sequence number from the message
            if id not in self.states:
                self.states[id]=0
                print("Receiver: new id:" +id)

            if self.states[id] == 0:
                if seq == 0:
                    self.ACK(0,addr)
                    self.states[id]=1
                    print("Receiver: "+id+' is now 1')
                    return bytes[1:],addr
                else:
                    self.ACK(1,addr)
            elif self.states[id] == 1:
                if seq == 1:
                    self.ACK(1,addr)
                    self.states[id]=0
                    print("Receiver: "+id+' is now 0')
                    return bytes[1:],addr
                else:
                    self.ACK(0,addr)


    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the just received packet
    # If resend is true, an ACK for the previous packet is sent, otherwise, a new ACK for the current packet is sent
    def ACK(self, ack_number,addr):
        data=str(ack_number).encode()
        self.socket.sendto(data,addr)
        print("Receiver: Sending ACK "+str(ack_number)+" id="+str(addr))
