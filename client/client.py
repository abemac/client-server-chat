from socket import *
from threading import Thread
import time


class Client:
    def __init__(self,serverip,serverport):
        self.serverip=serverip
        self.serverport=serverport
        self.socket=socket(AF_INET,SOCK_DGRAM)
        self.running=False
    def login(self):
        self.sendmessage('LOGIN user=abraham password=password')

    def start(self):
        self.running=True
        self.sendThread=Thread(target=self.sendLoop)
        self.sendThread.daemon=True
        self.sendThread.start()
        self.recvThread=Thread(target=self.recvLoop)
        self.recvThread.daemon=True
        self.recvThread.start()
        self.sendThread.join()
        self.recvThread.join()


    def sendLoop(self):
        while self.running==True:
            msg=input()
            self.sendmessage(msg)

    def recvLoop(self):
        while self.running==True:
            self.recvmessage()

    def sendmessage(self,message):
        formatted_msg='MESSAGE,abraham,"'+message.replace('"',"&quot;")+'"'
        self.socket.sendto(formatted_msg.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        msg,addr=self.socket.recvfrom(2048)
        print(msg.decode())

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    ip='127.0.0.1'
    port=12000
    client = Client(ip,port)
    client.start()
