import time

# This file contains the User, Message, and File classes. These classes are used by the ChatServer class in server.py.
# The classes contain the needed data members to manage logged in users, the messages they send or receive, and the
# files they send or recieve.

# Contains the username and network address of a user, as well as a method to print the data out.
class User:
    def __init__(self,username,addr):
        self.username=username
        self.addr=addr  # The network address of the user
    def __str__(self):
        return self.username+' '+str(self.addr)

# The package which a message is stored in. Contains the user who sent it, the contents of the message
# and the time it was sent.
class Message:
    def __init__(self,user_from,message):
        self.user_from=user_from
        self.message=message
        self.time=time.time()

# The package which a file from a file transfer is stored.
# Contains the username who sent the file, the raw content bytes of the file, the filename, and the file id
# (which is the time it was sent).
class File:
    def __init__(self,name,user_from,bytes):
        self.user_from=user_from
        self.bytes=bytes
        self.name=name
        self.id=str(time.time())
