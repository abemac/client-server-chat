import random
from socket import *
from threading import Thread,Timer
import time
import queue

# This file contains the code for the RDTSender and RDTReceiver classes.
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet loss is based on the percentage in the rdt.conf file.

# Send packet reliably over UDP
# The "states" of the sender are taken from Figure 3.15 in the Kurose-Ross text book
# The sender sends data and receives ACKs

class ConsoleLogger:
    def __init__(self,printlogs):
        self.printlogs=printlogs
    def log(self,str):
        if self.printlogs:
            print(str)

class RDTManager:
    def __init__(self,socket):
        f = open('rdt.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='PacketDropRate':
                self.packet_loss_percent=int(tokens[1])# Convert the string to an int
                                             # Percent chance any one packet being sent is lost due to simulated packet loss

        f.close()
        self.socket=socket
        self.logger=ConsoleLogger(False)

        self.acks=queue.Queue()
        self.data=queue.Queue()
        self.toapp = queue.Queue()
        self.sender=RDTSender(socket,self)
        self.receiver=RDTReceiver(socket,self)
        self.listener=Thread(target=self.listen)
        self.listener.daemon=True
        self.listener.start()


    def listen(self):
        while True:
            bytes,addr=self.socket.recvfrom(65536)
            if self.isACK(bytes):
                self.acks.put((bytes,addr))
            else:
                self.data.put((bytes,addr))


    def getACK(self):
        return self.acks.get()
    def getDATA(self):
        return self.data.get()

    def send(self,bytes,addr):
        self.sender.rdt_send(bytes,addr)
    def recv(self):
        return self.toapp.get()

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, pkt):
        if len(pkt) == 1:
            return True
        else:
            return False



    # Returns current time, in seconds, in string format
    # The 7 most significate seconds in epoch time are removed to make readability easier
    # Used for print our labling.
    def str_time(self):
        return "(" + str(time.time())[7:] + ")"

class RDTSender:

    def __init__(self,socket,manager):
        self.manager=manager
        self.socket=socket
        self.logger=manager.logger
        self.states={}#dictionary of active connection states
        self.timer=None
        self.timeout_value=.01
    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data
    def timeout(self,bytes,seqnum,addr):
        #self.logger.log("sender timout "+bytes.decode())
        self.udt_send(bytes,seqnum,addr)
        self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,seqnum,addr));
        self.timer.start()


    def rdt_send(self,bytes,addr):
        id=str(addr)
        print(self.str_time() + "Sender: sending to id: " + id)
        if id not in self.states:
            self.states[id]=0
            self.logger.log("Sender: new id "+id)
        if self.states[id]==0:
            self.udt_send(bytes,0,addr)
            self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,0,addr));
            self.timer.start()
            self.waitACK(0,id)
            self.timer.cancel()
            self.states[id]=1
            self.logger.log("Sender: State is now 1")
        elif self.states[id]==1:
            self.udt_send(bytes,1,addr)
            self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,1,addr));
            self.timer.start()
            self.waitACK(1,id)
            self.timer.cancel()
            self.states[id]=0
            self.logger.log("Sender: State is now 0")

    # Wait until ACK is received before moving to next state
    # Function will "block" until the sender has received the correct ACK
    def waitACK(self,ack_number,prev_id):
        self.logger.log("Sender "+prev_id+" waiting for ack " +str(ack_number))
        while True:
            bytes,addr=self.manager.getACK()
            ack_num = int(bytes[0:1]) # Extract the sequence number from the message
            id=str(addr)
            if id == prev_id and ack_num==ack_number:
                self.logger.log("Sender: Ack "+str(ack_number)+" Received")
                return
            else:
                print(self.str_time() + "Sender: INCORRECT ACK " + str(received_ack_num) + " (size=" + str(len(bytes)) + ") received")
                print(self.str_time() + "Sender: INCORRECT message contained: " + bytes.decode())

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, pkt):
        if len(pkt) == 1:
            return True
        else:
            return False

    # Receiver packets reliably over UDP
    # The receiver receives data and send ACKs
    def udt_send(self,bytes,seqnum,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            #self.logger.log("Sender dropping packet "+bytes.decode())
            return     # Packet is lost, don't actually send the packet
        else:
            #self.logger.log("Sender sending "+bytes.decode())
            seq_byte=str(seqnum).encode()
            data=b''.join([seq_byte,bytes])
            self.socket.sendto(data,addr)



class RDTReceiver:
    def __init__(self,socket,manager):
        self.logger=manager.logger
        self.states={} #dictionary of active connection states
        self.socket=socket
        self.manager=manager

        self.recvThread=Thread(target=self.rdt_recv)
        self.recvThread.daemon=True
        self.recvThread.start()

    def rdt_recv(self):
        while True:
            bytes,addr=self.manager.getDATA()   # Receive the UDP packet
            id=str(addr)
            print(self.str_time() + "Receiver: received from: " + id)
            print(self.str_time() + "Receiver: RECEIVED DATA: " + bytes.decode())
            seq = int(bytes[0:1]) # Extract the sequence number from the message

            if id not in self.states:
                self.states[id]=0
                print(self.str_time() + "Receiver: never received from this id before")

            if self.states[id] == 0:
                if seq == 0:
                    self.ACK(0,addr)
                    self.states[id]=1
                    self.manager.toapp.put((bytes[1:],addr))
                else:
                    print(self.str_time() + "Receiver: Incorrectly received seq num 1 (expecting 0); resending ACK 1")
                    self.ACK(1,addr)
            elif self.states[id] == 1:  # State 1 is for sending an ACK=1 for a received file
                print(self.str_time() + "Receiver: State is now 1 for " + id)
                if seq == 1:
                    self.ACK(1,addr)
                    self.states[id]=0
                    self.manager.toapp.put((bytes[1:],addr))
                else:
                    print(self.str_time() + "Receiver: Incorrectly received seq num 0 (expecting 1); resending ACK 0")
                    self.ACK(0,addr)


    # Construct the ACK packet and send the message with UDP; is udt protocol functions
    # This functions is used by the receiver to send an ACK for the just received packet
    def ACK(self, ack_number,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            self.logger.log("Reciever dropped ack "+str(ack_number))
            return     # Packet is lost, don't actually send the packet
        else:
            data=str(ack_number).encode()
            self.socket.sendto(data,addr)
            self.logger.log("Receiver: Sending ACK "+str(ack_number)+" id="+str(addr))
