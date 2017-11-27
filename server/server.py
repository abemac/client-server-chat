from socket import *
from util import *

# This file contains the code for the ChatServer class. The class contains functions that manage the current user,
# receive messages and file from users, and send the messages to every other user, and send the file to the correct user.
# This program is multi-threaded to allow the simultaneous sending and receiving of data.

class ChatServer:
    def __init__(self,port):
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',port))
        self.users=[]       # list of users of type User
        self.running=False  # Is the sever running and ready to send/receive data?
        self.files=[]       #buffer of files, of type File
        print("Chat server initiated")

    def start(self):
        self.running=True
        while self.running==True:
            bytes, clientaddress=self.socket.recvfrom(2048)
            self.handleMessage(bytes,clientaddress)

    def handleMessage(self,bytes,clientaddress):
        print(bytes)
        i=bytes.find(b' ',0)
        action=bytes[0:i].decode()

        if action == 'MESSAGE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()
            message=bytes[i+1:].decode()
            self.getUser(username).addr=clientaddress # Update User ip
            m=Message(username,message)
            self.sendMsg(m)
        elif action == 'LOGIN':
            username=bytes[i+1:].decode()
            self.addUser(username,clientaddress)
        elif action == 'FILE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()
            self.getUser(username).addr=clientaddress # Update User ip
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()
            filedata=bytes[i+1:]
            f=File(filename,username,filedata)
            self.files.append(f)
            self.askAboutFile(f)
        elif action == 'GET':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            fileid=bytes[lasti+1:i].decode()
            username=bytes[i+1:].decode()
            self.getUser(username).addr=clientaddress # Update User ip
            f=self.getFile(fileid)
            print(f.name)
            self.sendfile(f,self.getUser(username))


    def sendMsg(self,m):
        formatted_msg='MESSAGE '+m.user_from+' '+m.message
        for user in self.users:
            self.socket.sendto(formatted_msg.encode(),user.addr)

    def sendfile(self,f,user):
        formatted_msg='FILE '+f.name+' '
        msgbytes=formatted_msg.encode()
        bytestosend=b''.join([msgbytes,f.bytes])
        self.socket.sendto(bytestosend,user.addr)


    def askAboutFile(self,f):
        formatted_msg='FILE? '+f.name+' '+f.user_from+' '+f.id
        for user in self.users:
            if user.username != f.user_from:
                self.socket.sendto(formatted_msg.encode(),user.addr)

    def addUser(self,username,addr):
        if len(self.users) < 3:
            print(addr)
            newuser=User(username,addr)
            self.users.append(newuser)
        else:
            formatted_msg='ERROR chat server full';
            self.socket.sendto(formatted_msg.encode(),addr)

    def getUser(self,username):
        for user in self.users:
            if(user.username == username):
                return user
        return None

    def getFile(self,id):
        for file in self.files:
            if(file.id == id):
                return file
        return None

if __name__ == "__main__":
    port=12000
    chatserver = ChatServer(port)
    chatserver.start()
