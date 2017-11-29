import random
from socket import *
from threading import Thread,Timer
import time
import queue

class ConsoleLogger:
    def __init__(self,printlogs):
        self.printlogs=printlogs
    def log(self,str):
        if self.printlogs:
            print(str)
class UserBuffer:
    def __init__(self):
        self.self.acks=queue.Queue()


    def getACK(self):
        return self.acks.get()
    def getDATA(self):
        return self.data.get()





class RDTManager:
    def __init__(self,socket):
        f = open('rdt.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='PacketDropRate':
                self.packet_loss_percent=int(tokens[1])# Convert the string to an int
                                             # Percent chance any one packet being sent is lost due to simulated packet loss

        f.close()
        self.data=queue.Queue()
        self.socket=socket
        self.logger=ConsoleLogger(True)
        self.sender=RDTSender(socket,self)
        self.receiver=RDTReceiver(socket,self)
        self.userbuffers={}#diciontary id:UserBuffer
        self.listener=Thread(target=self.listen)
        self.listener.daemon=True
        self.listener.start()

    def listen(self):
        while True:
            bytes,addr=self.socket.recvfrom(65536)
            id=str(addr)
            if id not in self.userbuffers:
                self.userbuffers[id]=UserBuffer()
            self.userbuffers[id].put(bytes)

    def getACK(self,id):
        return self.userbuffers[id].getACK()
    def getDATA(self):
        return self.userbuffers[id].getDATA()

    def send(self,bytes,addr):
        self.sender.rdt_send(bytes,addr)
    def recv(self):
        return self.receiver.rdt_recv()

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def isACK(self, pkt):
        if len(pkt) == 1:
            return True
        else:
            return False



class RDTSender:

    def __init__(self,socket,manager):
        self.manager=manager
        self.socket=socket
        self.logger=manager.logger
        self.states={}#dictionary of active connection states
        self.timer=None
        self.timeout_value=0.1
    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data
    def timeout(self,bytes,seqnum,addr):
        self.udt_send(bytes,seqnum,addr)
        self.timer=Timer(self.timeout_value, self.timeout,args=(bytes,seqnum,addr));
        self.timer.start()

    def rdt_send(self,bytes,addr):
        id=str(addr)
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

    def waitACK(self,ack_number,prev_id):
        self.logger.log("Sender "+prev_id+" waiting for ack " +str(ack_number))
        while True:
            bytes,addr=self.manager.getACK(prev_id)
            ack_num = int(bytes[0:1]) # Extract the sequence number from the message
            if ack_num==ack_number:
                self.logger.log("Sender: Ack "+str(ack_number)+" Received")
                return


    def udt_send(self,bytes,seqnum,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            seq_byte=str(seqnum).encode()
            data=b''.join([seq_byte,bytes])
            self.socket.sendto(data,addr)



class RDTReceiver:
    def __init__(self,socket,manager):
        self.logger=manager.logger
        self.states={} #dictionary of active connection states
        self.socket=socket
        self.manager=manager

    def rdt_recv(self):
        while True:
            bytes,addr=self.manager.getDATA()   # Receive the UDP packet
            id=str(addr)
            seq = int(bytes[0:1]) # Extract the sequence number from the message
            if id not in self.states:
                self.states[id]=0

            if self.states[id] == 0:
                if seq == 0:
                    self.ACK(0,addr)
                    self.states[id]=1
                    return bytes[1:],addr
                else:
                    self.ACK(1,addr)
            elif self.states[id] == 1:
                if seq == 1:
                    self.ACK(1,addr)
                    self.states[id]=0
                    return bytes[1:],addr
                else:
                    self.ACK(0,addr)


    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the just received packet
    # If resend is true, an ACK for the previous packet is sent, otherwise, a new ACK for the current packet is sent
    def ACK(self, ack_number,addr):
        if random.randint(1, 100) <= self.manager.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            data=str(ack_number).encode()
            self.socket.sendto(data,addr)
            self.logger.log("Receiver: Sending ACK "+str(ack_number)+" id="+str(addr))
