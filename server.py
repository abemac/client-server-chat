from socket import *
from util import *
from threading import Thread
import sys
import signal
from rdt import *

# This file contains the code for the ChatServer class. The class contains functions that manage the current user,
# receive messages and file from users, and send the messages to every other user, and send the file to the correct user.
# This program is multi-threaded to allow the simultaneous sending and receiving of data.

class ChatServer:
    def __init__(self):
        f = open('server.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='Port':
                self.port=int(tokens[1])

        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',self.port))
        self.users=[]       # list of users of type User
        self.files=[]       #buffer of files, of type File
        signal.signal(signal.SIGINT,self.siginthandler)
        self.rdtsender=RDTSender(self.socket)
        self.rdtreceiver=RDTReceiver(self.socket)
        self.start()


    def start(self):
        self.mainthread=Thread(target=self.mainloop)
        self.mainthread.daemon=True
        self.mainthread.start()
        self.adminloop()
        self.mainthread.join()

    def adminloop(self):
        while True:
            cmd=''
            try:
                cmd=input('> ')
            except EOFError:
                print("")
                self.close()

            if cmd=='help':
                print ("""
    users - show current users
    files - show buffered files
    exit - stop the program
    help - show this help
                """)
            elif cmd == 'users':
                for user in self.users:
                    print (user)

            elif cmd == 'files':
                for file in self.files:
                    print (file.name)
            elif cmd == 'exit':
                self.close()

    def mainloop(self):
        while True:
            bytes, clientaddress=self.rdtreceiver.rdt_recv(65536)
            self.handleMessage(bytes,clientaddress)

    def handleMessage(self,bytes,clientaddress):
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
        elif action == 'LOGOUT':
            username=bytes[i+1:].decode()
            try:
                self.users.remove(self.getUser(username))
            except Exception:
                print("Error logging out user")
        elif action == 'FILE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()
            self.getUser(username).addr=clientaddress # Update User ip
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()
            filedata=bytes[i+1:]
            f=self.getFileByName(filename)
            if f == None:
                f=File(filename,username,filedata)
                self.files.append(f)
            else:
                f.bytes=b''.join([f.bytes,filedata]) #add on to file data
            if part=='LAST':
                self.askAboutFile(f)
        elif action == 'GET':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            fileid=bytes[lasti+1:i].decode()
            username=bytes[i+1:].decode()
            self.getUser(username).addr=clientaddress # Update User ip
            f=self.getFileById(fileid)
            self.sendfile(f,self.getUser(username))

    def sendMsg(self,m):
        formatted_msg='MESSAGE '+m.user_from+' '+m.message
        for user in self.users:
            self.sendbytes(formatted_msg.encode(),user.addr)

    def sendbytes(self,bytes,addr):
        self.rdtsender.rdt_send(bytes,addr)

    def sendfile(self,f,user):
        for i in range(0,len(f.bytes),10000):
            lastsegment=(i+10000) >= len(f.bytes)
            if lastsegment==True:
                formatted_msg='FILE LAST '+f.name+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,f.bytes[i:]])
                self.sendbytes(bytestosend,user.addr)
            elif i==0:#First segment
                formatted_msg='FILE FIRST '+f.name+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,f.bytes[i:i+10000]])
                self.sendbytes(bytestosend,user.addr)
            else:
                formatted_msg='FILE PART '+f.name+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,f.bytes[i:i+10000]])
                self.sendbytes(bytestosend,user.addr)


    def askAboutFile(self,f):
        formatted_msg='FILE? '+f.name+' '+f.user_from+' '+f.id
        for user in self.users:
            if user.username != f.user_from:
                self.sendbytes(formatted_msg.encode(),user.addr)

    def addUser(self,username,addr):
        if len(self.users) < 3:
            newuser=User(username,addr)
            self.users.append(newuser)
        else:
            formatted_msg='ERROR chat server full';
            self.sendbytes(formatted_msg.encode(),addr)

    def getUser(self,username):
        for user in self.users:
            if(user.username == username):
                return user
        return None

    def getFileById(self,id):
        for file in self.files:
            if(file.id == id):
                return file
        return None

    def getFileByName(self,name):
        for file in self.files:
            if(file.name == name):
                return file
        return None

    def close(self):
        self.socket.close()
        sys.exit(0)
    def siginthandler(self,signum,frame):
        print("")
        self.close()

if __name__ == "__main__":
    chatserver = ChatServer()
