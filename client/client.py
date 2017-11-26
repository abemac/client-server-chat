from socket import *
import time


class Client:
    def __init__(self,serverip,serverport):
        self.serverip=serverip
        self.serverport=serverport
        self.socket=socket(AF_INET,SOCK_DGRAM)

    def login(self):
        self.sendmessage('LOGIN: ')

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),server)

    def recvmessage(self):

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    ip='127.0.0.1'
    port=12000
    cleint = Client(ip,port)
    chatserver.start()
