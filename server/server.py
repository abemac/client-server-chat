from socket import *
from util import *
from csv import reader

class ChatServer:
    def __init__(self,port):
        self.msgsocket = socket(AF_INET,SOCK_DGRAM)
        self.msgsocket.bind(('',port))
        self.users=[] #list of users of type User
        self.running=False
        print("Chat server initiated")

        u=User('abraham')
        self.users+=u

    def start(self):
        self.running=True
        while self.running==True:
            message, clientaddress=self.msgsocket.recvfrom(2048)
            self.handleMessage(message.decode(),clientaddress)

    def handleMessage(self,string,clientaddress):
        for line in reader([string]):
            print(line)
            if line[0] == 'MESSAGE':
                user_from=line[1]
                message=line[2].replace('&quot;','\"');
                self.getUser(user_from).ipaddr=clientaddress #update User ip
                m=Message(user_from,user_to,message);


    def sendMsg(message):
        print ("NI")

    def addUser(self,username):
        newuser=User('abraham')
        self.users+=newuser

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
