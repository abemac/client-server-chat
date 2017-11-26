from socket import *
from threading import Thread
import time
from csv import reader
import tkinter as tk

class Client(tk.Frame):
    def __init__(self,serverip,serverport,master=None):
        super().__init__(master)
        self.pack()
        self.createWidgets()
        self.serverip=serverip
        self.serverport=serverport
        self.socket=socket(AF_INET,SOCK_DGRAM)
        self.running=False
    def createWidgets(self):
        self.textentry=tk.Text(self,height=3,width=40)
        self.textentry.pack(side="bottom")



        self.scrollbar=tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.msgs=tk.Listbox(self,yscrollcommand=self.scrollbar.set,width=40)

        self.msgs.pack(side=tk.LEFT,fill=tk.BOTH)
        self.scrollbar.config(command=self.msgs.yview)

        self.sendbtn = tk.Button(self, text="SEND", fg="red",
                               command=self.onSendBtnPress)
        self.sendbtn.pack(side="bottom")
    def say_hi(self):
        print("hi there, everyone!")
    def login(self,username):
        formatted_msg='LOGIN,'+username
        self.sendmessage(formatted_msg);
        self.username=username;
    def logout(self,username):
        formatted_msg='LOGOUT,'+username
        self.sendmessage(formatted_msg);

    def start(self):
        username=input("Please Enter Your Username: ")
        self.login(username)
        self.running=True
        #self.sendThread=Thread(target=self.sendLoop)
        #self.sendThread.daemon=True
        #self.sendThread.start()
        self.recvThread=Thread(target=self.recvLoop)
        self.recvThread.daemon=True
        self.recvThread.start()
        #self.sendThread.join()



    def onSendBtnPress(self):
            msg=self.textentry.get("1.0",tk.END)
            formatted_msg='MESSAGE,'+self.username+',"'+msg.replace('"',"&quot;")+'"'
            self.sendmessage(formatted_msg)

    def recvLoop(self):
        while self.running==True:
            self.recvmessage()

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        msg,addr=self.socket.recvfrom(2048)
        for line in reader([msg.decode()]):
            if line[0] == 'MESSAGE':
                username=line[1]
                message=line[2]
                if username == self.username:
                    self.msgs.insert(tk.END,("<b>You:</b> "+message.replace('&quot;','"').replace('\n','')))
                else:
                    self.msgs.insert(tk.END,(username+": "+message.replace('&quot;','"').replace('\n','')))
            elif line[0] == 'ERROR':
                message=line[2]
                print('SERVER ERROR: '+message);

    def close(self):
        self.socket.close()


if __name__ == "__main__":
    root=tk.Tk()
    ip='127.0.0.1'
    port=12000
    client = Client(ip,port,root)
    client.start()
    client.mainloop()
