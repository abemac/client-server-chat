import random
from socket import *
import threading


class RDTSender:

    def __init__(self,socket):
        self.socket=socket

    def rdt_send(self, bytes,addr):
        self.udt_send(bytes,addr)

    def udt_send(self,bytes,addr):
        self.socket.sendto(bytes,addr)

class RDTReceiver:
    def __init__(self,socket):
        self.state=0
        self.connection_states={} #dictionary of active connection states
        self.socket=socket
    def rdt_recv(self,bufsize):
            bytes,addr=self.socket.recvfrom(bufsize)   # Receive the UDP packet
            if not str(addr) in connections:
                connections_states[str(addr)]=0
            return bytes,addr
