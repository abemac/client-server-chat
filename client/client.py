from socket import *
from threading import Thread
import time
from csv import reader

class Client:
    def __init__(self,serverip,serverport):
        self.serverip=serverip
        self.serverport=serverport
        self.socket=socket(AF_INET,SOCK_DGRAM)
        self.running=False

    def login(self,username):
        formatted_msg='LOGIN,'+username
        self.sendmessage(formatted_msg);
        self.username=username;
    def logout(self,username):
        formatted_msg='LOGOUT,'+username
        self.sendmessage(formatted_msg);

    def start(self):
        username=input("Please Enter Your Username: ")
        self.login(username)
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
            formatted_msg='MESSAGE,'+self.username+',"'+msg.replace('"',"&quot;")+'"'
            self.sendmessage(formatted_msg)

    def recvLoop(self):
        while self.running==True:
            self.recvmessage()

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        msg,addr=self.socket.recvfrom(2048)
        for line in reader([msg.decode]):
            print(line)
            if line[0] == 'MESSAGE':
                username=line[1]
                message=line[2]
            elif line[0] == 'ERROR':
                username=line[1]
                self.addUser(username,clientaddress)

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    ip='127.0.0.1'
    port=12000
    client = Client(ip,port)
    client.start()
