from socket import *
from util import *
from csv import reader

# This file contains the code for the ChatServer class. The class contains functions that manage the current user,
# receive messages and file from users, and send the messages to every other user, and send the file to the correct user.
# This program is multi-threaded to allow the simultaneous sending and receiving of data.

class ChatServer:
    def __init__(self,port):
        self.msgsocket = socket(AF_INET,SOCK_DGRAM)
        self.msgsocket.bind(('',port))
        self.users=[]       # list of users of type User
        self.running=False  # Is the sever running and ready to send/receive data?
        print("Chat server initiated")

    def start(self):
        self.running=True
        while self.running==True:
            message, clientaddress=self.msgsocket.recvfrom(2048)
            self.handleMessage(message.decode(),clientaddress)

    def handleMessage(self,string,clientaddress):
        for line in reader([string]):
            print(line)
            if line[0] == 'MESSAGE':
                username=line[1]
                message=line[2]
                self.getUser(username).addr=clientaddress # Update User ip
                m=Message(username,message)
                self.sendMsg(m)
            elif line[0] == 'LOGIN':
                username=line[1]
                self.addUser(username,clientaddress)

    def sendMsg(self,m):
        formatted_msg='MESSAGE,'+m.user_from+',"'+m.message+'"'
        for user in self.users:
            self.msgsocket.sendto(formatted_msg.encode(),user.addr)

    def addUser(self,username,addr):
        if len(self.users) < 3:
            print(addr)
            newuser=User(username,addr)
            self.users.append(newuser)
        else:
            formatted_msg='ERROR,chat server full';
            self.msgsocket.sendto(formatted_msg.encode(),addr)

    def getUser(self,username):
        for user in self.users:
            if(user.username == username):
                return user
        return None

    def startConversation(self,users):
        c=Conversation()
        for user in users:
            c.addParticipant()


if __name__ == "__main__":
    port=12000
    chatserver = ChatServer(port)
    chatserver.start()
