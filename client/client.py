from socket import *
import time


class Client:
    def __init__(self,serverip,serverport):
        self.serverip=serverip
        self.serverport=serverport
        self.socket=socket(AF_INET,SOCK_DGRAM)

    def login(self):
        self.sendmessage('LOGIN user=abraham password=password')

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        print("not implemented")

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    ip='127.0.0.1'
    port=12000
    client = Client(ip,port)
    client.login()
