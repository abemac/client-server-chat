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
# The sender sends data and receives ACKs
class RDTSender:

    def __init__(self,socket):
        self.socket=socket
        self.states={}  # Dictionary of active connection states


    # Called by the application to send a packet reliably over the UDP connection
    # The sender can only send a new message if has already received the previously sent packet
    def rdt_send(self, bytes, addr):
        id=str(addr)
        print("Sender: sending with id: " + id)
        if id not in self.states:
            self.states[id]=0
            print("Sender: this is a new id")
        if self.states[id]==0:  # State 0 is the for sending packet with seq # 0
            self.udt_send(bytes,0,addr) # Send the packet with seq # 0
            self.waitACK(0,id)  # Wait for ACK = 0
            self.states[id]=1   # State 1 is the for sending packet with seq # 1
            print("Sender: State is now 1")
        elif self.states[id]==1:
            self.udt_send(bytes,1,addr) # Send the packet with seq # 0
            self.waitACK(1,id)
            self.states[id]=0
            print("Sender: State is now 0")


    # Wait until ACK is received before moving to next state
    # Function will "block" until the sender has received the correct ACK
    def waitACK(self, ack_number, prev_id):
        print("Sender " + prev_id + " waiting for ack " + str(ack_number))
        while True:
            bytes,addr=self.socket.recvfrom(2048) # Get the payload
            received_ack_num = int(bytes[0:1]) # Extract the ACK number from the message
            id=str(addr)
            print("Sender: received ACK from: " + id)
            if id == prev_id and self.isACK(bytes) and received_ack_num == ack_number:
                print("Sender: CORRECT ACK " + str(ack_number) + " received")   # The ACK number is the expected one for the current state, accept it
                return
            else:
                print("Sender: INCORRECT ACK " + str(received_ack_num) + " (size=" + len(bytes) + ") received")
                print("Sender: was expecting ACK num:, " + ack_number)


    # Send the packet of the unreliable connection
    def udt_send(self,bytes,seqnum,addr):
        seq_byte=str(seqnum).encode()   # Add the sequence number to the data
        data=b''.join([seq_byte,bytes])
        print("Sender: UDT sending data to id=" + str(addr) + ": " + data.decode())
        self.socket.sendto(data, addr)   # Send the data

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
# The receiver receives data and send ACKs
class RDTReceiver:
    def __init__(self,socket):
        self.states={} #dictionary of active connection states
        self.socket=socket


    # Receive the UDP packet
    # Function will "block" until a message with the expected sequence number is received
    # If the correct sequence number is received, it send and ACK for it and send the bytes to the application
    # If the incorrect sequence number is received, it will resend the previous ACK
    def rdt_recv(self,bufsize):
        while True:
            bytes,addr=self.socket.recvfrom(bufsize)   # Get packet from buffer
            id=str(addr)
            print("Receiver: received from: " + id)
            print("Receiver: received data: " + bytes.decode())
            seq = int(bytes[0:1]) # Extract the sequence number from the message

            if id not in self.states:
                self.states[id]=0

            if self.states[id] == 0:
                print("Receiver state is 0")
                if seq == 0:                # State 0 is for sending an ACK=0 for a received file
                    print("Receiver: CORRECTLY received seq num 0")
                    self.ACK(0,addr)        # Send ACK=0
                    self.states[id]=1       # Increment the state
                    return bytes[1:],addr   # Return the bytes to the application
                else:
                    print("Receiver: Incorrectly received seq num 1 (expecting 0); resending ACK 1")
                    self.ACK(1,addr)
            elif self.states[id] == 1:  # State 1 is for sending an ACK=1 for a received file
                print("Receiver state is 1")
                if seq == 1:
                    print("Receiver: CORRECTLY received seq num 1")
                    self.ACK(1,addr)        # Send ACK=1
                    self.states[id]=0       # Increment the state
                    return bytes[1:],addr   # Return the bytes to the application
                else:
                    print("Receiver: Incorrectly received seq num 0 (expecting 1); resending ACK 0")
                    self.ACK(0,addr)


    # Construct the ACK packet and send the message with UDP; is udt protocol functions
    # This functions is used by the receiver to send an ACK for the just received packet
    def ACK(self, ack_number,addr):
        data=str(ack_number).encode()
        self.socket.sendto(data,addr)
        print("Receiver: Sending ACK " + str(ack_number) + " to id="+str(addr))

        # Packet loss example, would be applied to the sending the ACK as well.
        # if random.randint(1, 100) <= self.packet_loss_percent:
        #     return     # Packet is lost, don't actually send the packet
        # else:
        #     # send the packet over UDP
        #     seq_byte=str(seq_number).encode()
        #     data=b''.join([seq_byte,bytes])
        #     self.socket.sendto(data,addr)