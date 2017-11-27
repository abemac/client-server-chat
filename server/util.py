import time

# The file contains the User and Message classes. These classes are used by the ChatServer class in server/server.py.
# The classes contain the needed data members to manage logged in users and the messages they send or receive.

class User:
    def __init__(self,username,addr):
        self.username=username
        self.addr=addr;

class Message:
    def __init__(self,user_from,message):
        self.user_from=user_from
        self.message=message
        self.time=time.time()
