from socket import *
from util import *
from threading import Thread
import sys
import signal
from rdt import *

# This file contains the code for the ChatServer class. The class contains functions that manage the current users,
# receive messages and files from users, send the messages/files to every other user.
# This program is multi-threaded to allow the simultaneous sending and receiving of data.

class ChatServer:
    def __init__(self):
        f = open('server.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='Port':
                self.port=int(tokens[1])    # Get the default port number from server.conf
        f.close()

        # Open up two sockets: one for sending, and one for receiving
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',self.port))

        self.users=[]       # list of users currently logged in; of type User
        self.files=[]       # buffer of files receivedl; of type File
        signal.signal(signal.SIGINT,self.siginthandler)
        self.rdtsender=RDTSender(self.socket)       # Objects used to send and receive
        self.rdtreceiver=RDTReceiver(self.socket)   # data reliably over the UDP connection
        self.start()

    # Starts the varous threads needed to run the program, including the server command line interface
    # and the sending and receiving of data
    def start(self):
        self.mainthread=Thread(target=self.mainloop)
        self.mainthread.daemon=True
        self.mainthread.start()
        self.adminloop()
        self.mainthread.join()

    # Handles the server command line interface
    def adminloop(self):
        while True:
            cmd=''
            try:
                cmd=input('> ')         # Get the user input
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
            elif cmd == 'users':        # Print out the currently logged in users
                for user in self.users:
                    print (user)

            elif cmd == 'files':        # Print the currently buffered files sent from users
                for file in self.files:
                    print (file.name)
            elif cmd == 'exit':         # Close the server program
                self.close()

    # Handles the receiving of data sent by users passed up from the rdt protocol
    def mainloop(self):
        while True:
            bytes, clientaddress=self.rdtreceiver.rdt_recv(65536)   # Get data from rdt level
            print("Server.py: "+bytes.decode())
            #bytes, clientaddress=self.socket.recvfrom(65536)
            self.handleMessage(bytes,clientaddress)                 # Process the received message

    # Handles the messages (packets) sent by user, depending on the type of message they sent
    def handleMessage(self,bytes,clientaddress):
        i=bytes.find(b' ',0)
        action=bytes[0:i].decode()      # Extract the action type of the raw received bytes

        if action == 'MESSAGE':         # The user sent a chat message, which is to be sent to everyone elses
            lasti=i
            i=bytes.find(b' ',lasti+1)  # Extracts the starting point of the payload
            username=bytes[lasti+1:i].decode()  # Extracts the username from the payload
            message=bytes[i+1:].decode()        # Extracts the chat message from the payload
            self.getUser(username).addr=clientaddress # Updates User's IP address
            m=Message(username,message)         # Create a new message container
            self.sendMsg(m)                     # Broadcast the message to every user
        elif action == 'LOGIN':         # Message sent from a user who just logged uin
            username=bytes[i+1:].decode()
            self.addUser(username,clientaddress)    # Add the new user to the list of logged in users
        elif action == 'LOGOUT':        # Message sent when a user logs out
            username=bytes[i+1:].decode()
            try:
                self.users.remove(self.getUser(username))   # Remove the username from the list of logged in users
            except Exception:
                print("Error logging out user")
        elif action == 'FILE':          # The user is uploading a file
            lasti=i                     # These i and lasti values are used to segement the message for data extraction
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()  # Get the part identifier, (is it the last segemnt of the file)
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()  # Extract the username of the user who is sending the file
            self.getUser(username).addr=clientaddress # Update User ip
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Extract the filename
            filedata=bytes[i+1:]                # Extract the file data
            f=self.getFileByName(filename)      # See if part of the file is already received
            if f == None:
                f=File(filename,username,filedata)  # No file found, create a new container for one
                self.files.append(f)
            else:
                f.bytes=b''.join([f.bytes,filedata]) # Add on to file data if the server aready has a record of it
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
        #self.socket.sendto(bytes,addr);

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
