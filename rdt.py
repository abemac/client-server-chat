import random
from socket import *
import threading
import time

# This file contains the code for the RDTSender and RDTReceiver classes.
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet loss is based on the percentage in the rdt.conf file.

# Send packet reliably over UDP
# The "states" of the sender are taken from Figure 3.15 in the Kurose-Ross text book
class RDTSender:

    def __init__(self,socket):
        self.socket=socket
        self.states={} #dictionary of active connection states

    # Called by the application to send a packet reliably over the UDP connection
    # The sender can only send a new message if has already received the previously sent packet
    def rdt_send(self, bytes,addr):
        id=str(addr)
        if id not in self.states:
            self.states[id]=0
            print("Sender: new id "+id)
        if self.states[id]==0:  # State 0 is the for sending packet with seq # 0
            self.udt_send(bytes,0,addr) # Send the packet with seq # 0
            self.waitACK(0,id)  # WWait for ACK = 0
            self.states[id]=1   # State 1 is the for sending packet with seq # 1
            print("Sender: State is now 1")
        elif self.states[id]==1:
            self.udt_send(bytes,1,addr) # Send the packet with seq # 0
            self.waitACK(1,id)
            self.states[id]=0
            print("Sender: State is now 0")

    # Wait until ACK is received before moving to next state 
    def waitACK(self,ack_number,prev_id):
        print("Sender "+prev_id+" waiting for ack " +str(ack_number))
        while True:
            bytes,addr=self.socket.recvfrom(2048) # Get the payload
            ack_num = int(bytes[0:1]) # Extract the sequence number from the message
            id=str(addr)
            if id == prev_id and self.isACK(bytes) and ack_num==ack_number:
                print("Sender: Ack "+str(ack_number)+" Received")   # The ACK number is the expected one for the current state, accept it
                return

    # Send the packet of the unreliable connection
    def udt_send(self,bytes,seqnum,addr):
        seq_byte=str(seqnum).encode()   # Add the sequence number to the data
        data=b''.join([seq_byte,bytes])
        print("Sender: sending "+data.decode())
        self.socket.sendto(data,addr)   # Send the data

        # We do have an implementation for packet loss;
        # if random.randint(1, 100) <= self.packet_loss_percent:
        #     return     # Packet is lost, don't actually send the packet
        # else:
        #     # send the packet over UDP
        #     seq_byte=str(seq_number).encode()
        #     data=b''.join([seq_byte,bytes])
        #     self.socket.sendto(data,addr)


    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, ack):
        if len(ack) == 1:
            return True
        else:
            return False

# Receiver packets reliably over UDP
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

            if self.states[id] == 0:
                if seq == 0:    # State 0 is for sending an ACK=0 for a received file
                    self.ACK(0,addr)    #Send ACK=0
                    self.states[id]=1   # Increment the state
                    return bytes[1:],addr
                else:
                    self.ACK(1,addr)
            elif self.states[id] == 1:  # State 1 is for sending an ACK=1 for a received file
                if seq == 1:
                    self.ACK(1,addr)    # Send ACK=1
                    self.states[id]=0   # Increment the state
                    return bytes[1:],addr
                else:
                    self.ACK(0,addr)


    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the just received packet
    def ACK(self, ack_number,addr):
        data=str(ack_number).encode()
        self.socket.sendto(data,addr)
        print("Receiver: Sending ACK "+str(ack_number)+" id="+str(addr))

        # Packet loss example, would be applied to the sending the ACK as well.
        # if random.randint(1, 100) <= self.packet_loss_percent:
        #     return     # Packet is lost, don't actually send the packet
        # else:
        #     # send the packet over UDP
        #     seq_byte=str(seq_number).encode()
        #     data=b''.join([seq_byte,bytes])
        #     self.socket.sendto(data,addr)
