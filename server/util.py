from hashlib import md5
import time

def gethash(string):
    m=md5()
    m.update(string.encode())
    return m.hexdigest()

class Conversation:
    def __init__(self):
        self.participants=[] #list of participants of type User
        self.messages=[] #list of messages

    def addParticipant(user):
        self.participants+=user

class User:
    def __init__(self,username,password='',ipaddr=''):
        self.username=username
        self.pwd_hash=util.gethash(password)

class Message:
    def __init__(self,user,message):
        self.user=user
        self.message=message
        self.time=time.time()
