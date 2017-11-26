from socket import *
from types import *

class ChatServer:

    def __init__(self,port):
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',port))
        self.users=[] #list of users of type User
        self.conversations=[] #list of conversations of type Conversation
        self.running=False
        print("Chat server initiated")


    def start(self):
        self.running=True
        while self.running==True:
            data, clientaddress=socket.recvfrom(2048)
            print(data.decode())

    def addUser(self,username,password=''):
        newuser=User('abraham','password')
        self.users+=newuser

    def startConversation(self,users):
        c=Conversation()
        for user in users:
            c.addParticipant()


if __name__ == "__main__":
    port=12000
    chatserver = ChatServer(port)
    chatserver.start()
