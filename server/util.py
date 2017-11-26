import time
class User:
    def __init__(self,username,ipaddr=''):
        self.username=username
        self.ipaddr=ipaddr;

class Message:
    def __init__(self,user_from,message):
        self.user_from=user_from
        self.message=message
        self.time=time.time()
