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

        # Open and bind the socket(s) need for the server to communicate
        self.socket = socket(AF_INET,SOCK_DGRAM)
        self.socket.bind(('',self.port))

        self.users=[]       # list of users currently logged in; of type User
        self.files=[]       # buffer of files receivedl; of type File
        signal.signal(signal.SIGINT,self.siginthandler)
        self.rdt=RDTManager(self.socket)       # Objects used to send and receive
        self.start()

    # Starts the various threads needed to run the program, including the server command line interface
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

            if cmd=='help':             # Print out the help message
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
            bytes, clientaddress=self.rdt.recv()   # Get data from rdt level
            #bytes, clientaddress=self.socket.recvfrom(65536)
            self.handleMessage(bytes,clientaddress)                 # Process the received message

    # Handles the messages (packets) sent by user, depending on the type of message they sent
    def handleMessage(self,bytes,clientaddress):
        i=bytes.find(b' ',0)            # These i and lasti values are used to segment the message for data extraction
        action=bytes[0:i].decode()      # Extract the action type of the raw received bytes

        if action == 'MESSAGE':         # The user sent a chat message, which is to be sent to everyone elses
            lasti=i
            i=bytes.find(b' ',lasti+1)                  # Extracts the starting point of the payload
            username=bytes[lasti+1:i].decode()          # Extracts the username from the payload
            message=bytes[i+1:].decode()                # Extracts the chat message from the payload
            self.getUser(username).addr=clientaddress   # Updates User's IP address
            m=Message(username,message)                 # Create a new message container
            self.sendMsg(m)                             # Broadcast the message to every user
        elif action == 'LOGIN':     # Message sent from a user who just logged uin
            username=bytes[i+1:].decode()
            self.addUser(username,clientaddress)  # Add the new user to the list of logged in users
        elif action == 'LOGOUT':    # Message sent when a user logs out
            username=bytes[i+1:].decode()
            try:
                self.users.remove(self.getUser(username))   # Remove the username from the list of logged in users
            except Exception:
                print("Error logging out user")
        elif action == 'FILE':          # The user is uploading a file
            lasti=i                     # These i and lasti values are used to segment the message for data extraction
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()  # Get the part identifier, (is it the last segment of the file)
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()          # Extract the username of the user who is sending the file
            self.getUser(username).addr=clientaddress   # Update User ip
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Extract the filename
            filedata=bytes[i+1:]                # Extract the file data
            f=self.getFileByName(filename)      # See if part of the file is already received
            if f == None:
                f=File(filename,username,filedata)  # No file found, create a new container for one
                self.files.append(f)
            else:
                f.bytes=b''.join([f.bytes,filedata]) # Add on to file data if the server already has a record of it
            if part=='LAST':            # All segments of the file have been received
                self.askAboutFile(f)    # Ask the other users if they would like to receive the file
        elif action == 'GET':   # User is asking for a file from the server
            lasti=i
            i=bytes.find(b' ',lasti+1)
            fileid=bytes[lasti+1:i].decode()    # Get the file id
            username=bytes[i+1:].decode()       # Get the username of person who wants to receive the file
            self.getUser(username).addr=clientaddress   # Update User ip
            f=self.getFileById(fileid)
            self.sendfile(f,self.getUser(username))     # Send the file to the user

    # Broadcasts a chat message to every user connected to the server
    def sendMsg(self,m):
        formatted_msg='MESSAGE '+m.user_from+' '+m.message      # Crafts the payload into our standard format
        for user in self.users:
            self.sendbytes(formatted_msg.encode(),user.addr)    # Loops through all the users and send them the message

    # The interface between the application and the application and the rdt protocol
    # This is called whenever a the server needs to send a message
    def sendbytes(self,bytes,addr):
        self.rdt.send(bytes,addr)
        #self.socket.sendto(bytes,addr);

    # Breaks up a file and send it in segments
    def sendfile(self,f,user):
        for i in range(0,len(f.bytes),10000):
            lastsegment=(i+10000) >= len(f.bytes)
            if lastsegment==True:                       # This segment is the final part of the file
                formatted_msg='FILE LAST '+f.name+' '   # Crafts the payload into our standard format
                msgbytes=formatted_msg.encode()         # Convert the message to raw bytes
                bytestosend=b''.join([msgbytes,f.bytes[i:]])    # Add the file data bytes to the payload
                self.sendbytes(bytestosend,user.addr)   # Send the bytes over the rdt protocol
            elif i==0:                                  # First segment of the file
                formatted_msg='FILE FIRST '+f.name+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,f.bytes[i:i+10000]])
                self.sendbytes(bytestosend,user.addr)
            else:                                       # This segment is a middle part of the file
                formatted_msg='FILE PART '+f.name+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,f.bytes[i:i+10000]])
                self.sendbytes(bytestosend,user.addr)

    # Broadcast to every user if they want to receive the file, except to the person who sent the file
    def askAboutFile(self,f):
        formatted_msg='FILE? '+f.name+' '+f.user_from+' '+f.id  # Crafts the payload into our standard format
        for user in self.users:
            if user.username != f.user_from:
                self.sendbytes(formatted_msg.encode(),user.addr)

    # Adds a new user to the server's list of logged in users
    def addUser(self,username,addr):
        if len(self.users) < 3:
            newuser=User(username,addr)     # Create the new user and add them to the list
            self.users.append(newuser)
        else:                               # There can only be a max of three users on the server at once
            formatted_msg='ERROR chat server full'
            self.sendbytes(formatted_msg.encode(),addr)

    # Returns the user data from a given username
    def getUser(self,username):
        for user in self.users:
            if(user.username == username):
                return user
        return None

    # Return a file from a given file id
    def getFileById(self,id):
        for file in self.files:
            if(file.id == id):
                return file
        return None

    # Return a file from a given file name
    def getFileByName(self,name):
        for file in self.files:
            if(file.name == name):
                return file
        return None

    # When the server exits, close the sockets
    def close(self):
        self.socket.close()
        sys.exit(0)
    
    # Handles system signals
    def siginthandler(self,signum,frame):
        print("")
        self.close()

# Starts the Chat server when this file is run
if __name__ == "__main__":
    chatserver = ChatServer()
