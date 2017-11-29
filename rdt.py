import random
from socket import *
from threading import Thread,Timer
import time
import queue

# This file contains the Console Logger, RDTManager, RDTSender, RDTReceiver class
# These class act as the interface between the application and the network
# The applications use manager to send and receive data and the RDTSender and RDTReceiver class act as helpers for the Manager
# to actually send and receive data.

# Print debugging message to the console
class ConsoleLogger:
    def __init__(self,printlogs):
        self.printlogs=printlogs
    def log(self,str):
        if self.printlogs:
            print(str)

# The main interface between the application and the network. This class creates a thread to manage the receiving simultaneously with the sending of messages
# It also keeps a buffer of the sent and received packet to send up to the application layer
class RDTManager:
    def __init__(self,socket):
        f = open('rdt.conf')    # Open rdt.conf to extract the packet drop rate constant
        for line in f:
            tokens=line.split()
            if tokens[0]=='PacketDropRate':
                self.packet_loss_percent=int(tokens[1]) # Convert the string to an int
                                                        # This is the percent chance any one packet being sent is lost due to simulated packet loss
        f.close()
        self.socket=socket      # Set the socket as the same socket from the application layer
        self.logger=ConsoleLogger(False)

        self.acks=queue.Queue()     # Buffer of ACKs received
        self.data=queue.Queue()     # Buffer of data received
        self.toapp = queue.Queue()  # Buffer of data to the application
        self.sender=RDTSender(socket,self)  # Objects that manage the actual sending and receiving
        self.receiver=RDTReceiver(socket,self)
        self.listener=Thread(target=self.listen)    # Create thread to receive from UDP socket
        self.listener.daemon=True
        self.listener.start()

    # Thread listens for data comming in on UDP socket
    def listen(self):
        while True:
            bytes,addr=self.socket.recvfrom(65536)
            if self.isACK(bytes):
                self.acks.put((bytes,addr)) # Store ACK in the ACK buffer
            else:
                self.data.put((bytes,addr)) # Store data in the data buffer

    # Helper functions for the RDTSender and RDTReceiver
    def getACK(self):
        return self.acks.get()
    def getDATA(self):
        return self.data.get()
    
    # USed by application layer send data
    def send(self,bytes,addr):
        self.sender.rdt_send(bytes,addr)
    # USed by application layer get data from buffer
    def recv(self):
        return self.toapp.get()

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, pkt):
        if len(pkt) == 1:
            return True
        else:
            return False

# Sends data over the UDP socket reliably and manages sender state
# Waits for ACK from receiver after sending data
# Based of RDTSender3.0 from the text book
class RDTSender:
    def __init__(self,socket,manager):
        self.manager=manager    # Use the manager to get ACKs
        self.socket=socket      # Use the socket passed down from the application interface
        self.logger=manager.logger
        self.states={}          # dictionary of active connection states
        self.timer=None         # Timer used to detect timeouts
        self.timeout_value=.01  # When the timer timesout

    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data
    def timeout(self,bytes,seqnum,addr):
        #self.logger.log("sender timout "+bytes.decode())
        self.udt_send(bytes,seqnum,addr)
        self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,seqnum,addr)) 
        self.timer.start()  # Restart the timeout timer

    # Send data with proper sequence number based on the current state
    def rdt_send(self,bytes,addr):
        id=str(addr)
        if id not in self.states:   # If this sender has never sent before, add it dictionary
            self.states[id]=0
            self.logger.log("Sender: new id "+id)
        if self.states[id]==0:  
            self.udt_send(bytes,0,addr) # Send the packet is sequence number 0
            self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,0,addr)) # Create the timeout timer
            self.timer.start()  # Start the timeout timer
            self.waitACK(0,id)  # Wait for ACK to be received
            self.timer.cancel() # Stop timeout timer
            self.states[id]=1   # Move to the next state
            self.logger.log("Sender: State is now 1")
        elif self.states[id]==1:
            self.udt_send(bytes,1,addr) # Send the packet is sequence number 0
            self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,1,addr));
            self.timer.start()
            self.waitACK(1,id)
            self.timer.cancel()
            self.states[id]=0
            self.logger.log("Sender: State is now 0")

    # Sender waits in this function until it has received the proper ACK number
    def waitACK(self,ack_number,prev_id):
        self.logger.log("Sender "+prev_id+" waiting for ack " +str(ack_number))
        while True:
            bytes,addr=self.manager.getACK()    # Get the ACK data from the manager
            ack_num = int(bytes[0:1])           # Extract the sequence number from the message
            id=str(addr)
            if id == prev_id and ack_num==ack_number:   # Check to see if ACK is the correct number
                self.logger.log("Sender: Ack "+str(ack_number)+" Received")
                return  # Sender received the correct ACK and can move on

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, pkt):
        if len(pkt) == 1:
            return True
        else:
            return False

    # Send the data over the UDP connection
    # This function also simulates random packet loss
    def udt_send(self,bytes,seqnum,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            #self.logger.log("Sender dropping packet "+bytes.decode())
            return     # Packet is lost, don't actually send the packet
        else:
            #self.logger.log("Sender sending "+bytes.decode())
            seq_byte=str(seqnum).encode()   # Encode the packet
            data=b''.join([seq_byte,bytes]) # Add sequence number to the packet
            self.socket.sendto(data,addr)   # Send packet over the UDP connection

# Receives data over the UDP connection and sends back and ACK to the sender
# Based on RDTReceiver2.2 from the text book
class RDTReceiver:
    def __init__(self,socket,manager):
        self.logger=manager.logger
        self.states={}      # dictionary of active connection states
        self.socket=socket  # Use the socket passed down from the application interface
        self.manager=manager    # Use the manager to get data from the UDP socket

        # Create and start a thread that will work independently to receive new data
        self.recvThread=Thread(target=self.rdt_recv)
        self.recvThread.daemon=True
        self.recvThread.start()

    # Main loop function of the recvThread
    # Extracts the data from packet, sees if it has a valid sequence number and pushes the
    # data to a buffer for the applation layer
    def rdt_recv(self):
        while True:
            bytes,addr=self.manager.getDATA()   # Receive the UDP packet
            id=str(addr)
            seq = int(bytes[0:1]) # Extract the sequence number from the message
            if id not in self.states:# If this receiver has never receivered before, add it dictionary
                self.states[id]=0

            if self.states[id] == 0:
                if seq == 0:
                    self.ACK(0,addr)    # Send ACK number 0
                    self.states[id]=1   # Change state
                    self.manager.toapp.put((bytes[1:],addr))    # Push data to buffer
                else:
                    self.ACK(1,addr)    # Out of order packer received, resend the old ACK
            elif self.states[id] == 1:
                if seq == 1:
                    self.ACK(1,addr)    # Send ACK number 0
                    self.states[id]=0   # Change state
                    self.manager.toapp.put((bytes[1:],addr))  # Push data to buffer
                else:
                    self.ACK(0,addr)    # Out of order packer received, resend the old ACK


    # This functions is used by the receiver to send an ACK for the just received packet
    # This function also simulates random packet loss
    def ACK(self, ack_number,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            self.logger.log("Reciever dropped ack "+str(ack_number))
            return     # Packet is lost, don't actually send the packet
        else:
            data=str(ack_number).encode()   # Encode the ACK number in packet
            self.socket.sendto(data,addr)   # Send ACK over the UDP socket
            self.logger.log("Receiver: Sending ACK "+str(ack_number)+" id="+str(addr))
