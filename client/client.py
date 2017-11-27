from socket import *
from threading import Thread
import time
from csv import reader
import tkinter as tk
import tkinter.filedialog as filechooser
import os

# This file contains the code for the Client class. The class contains functions that create the user interface,
# allow a user to login or out, and manage the sending and receiving of files and messages. This program is multi-threaded
# to allow the simultaneous sending and receiving of data.

class Client(tk.Frame):
    def __init__(self,root):
        super().__init__(root)
        self.pack()
        self.createLoginWidgets()
        self.serverport=12000
        self.socket=socket(AF_INET,SOCK_DGRAM)
        self.running=False
        self.loggedin=False

    def createLoginWidgets(self):
        self.l1=tk.Label(self, text="Server IP:")
        self.l1.grid(row=0)
        self.l2=tk.Label(self, text="Alias:")
        self.l2.grid(row=1)
        self.ip = tk.Entry(self)
        self.ip.grid(row=0, column=1)
        self.uname = tk.Entry(self)
        self.uname.grid(row=1, column=1)
        self.connectBtn = tk.Button(self, text="Connect", fg="red",command=self.onConnect)
        self.connectBtn.grid(row=2,column=1)

    def onConnect(self):
        self.serverip = str(self.ip.get())
        self.username = str(self.uname.get())
        self.ip.destroy()
        self.uname.destroy()
        self.l1.destroy()
        self.l2.destroy()
        self.connectBtn.destroy()
        self.login(self.username)
        self.createMainWidgets()
        self.start()

    def createMainWidgets(self):
        self.sendfilebtn = tk.Button(self, text="SEND FILE", fg="red",command=self.onSendfileBtnPress)
        self.sendfilebtn.pack(side="bottom")

        self.sendbtn = tk.Button(self, text="SEND", fg="red",command=self.onSendBtnPress)
        self.sendbtn.pack(side="bottom")

        self.textentry=tk.Text(self,height=3,width=40)
        self.textentry.pack(side="bottom")

        self.scrollbar=tk.Scrollbar(self)
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.msgs=tk.Listbox(self,yscrollcommand=self.scrollbar.set,width=40)

        self.msgs.pack(side=tk.LEFT,fill=tk.BOTH)
        self.scrollbar.config(command=self.msgs.yview)

    def onSendBtnPress(self):
        msg=self.textentry.get("1.0",tk.END)
        self.textentry.delete("1.0",tk.END)
        formatted_msg='MESSAGE,'+self.username+',"'+msg.replace('"',"&quot;")+'"'
        self.sendmessage(formatted_msg)

    def onSendfileBtnPress(self):
        filetosend=filechooser.askopenfilename()
        filesize=os.path.getsize(filetosend)
        f=open(filetosend,'rb')
        bytes=f.read(filesize)
        print(bytes)
        self.sendfile(bytes)

    def login(self,username):
        formatted_msg='LOGIN,'+username
        self.sendmessage(formatted_msg)

    def logout(self,username):
        formatted_msg='LOGOUT,'+username
        self.sendmessage(formatted_msg)

    def start(self):
        self.running=True
        self.recvThread=Thread(target=self.recvLoop)
        self.recvThread.daemon=True
        self.recvThread.start()

    def recvLoop(self):
        while self.running==True:
            self.recvmessage()

    def sendfile(self,data):
        formatted_msg='FILE,'+self.username+','
        msgbytes=formatted_msg.encode()
        bytestosend=b''.join([msgbytes,data])
        self.socket.sendto(bytestosend,(self.serverip,self.serverport))

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        msg,addr=self.socket.recvfrom(2048)
        for line in reader([msg.decode()]):
            if line[0] == 'MESSAGE':
                username=line[1]
                message=line[2]
                if username == self.username:
                    self.msgs.insert(tk.END,("You: "+message.replace('&quot;','"').replace('\n','')))
                else:
                    self.msgs.insert(tk.END,(username+": "+message.replace('&quot;','"').replace('\n','')))
            elif line[0] == 'ERROR':
                message=line[2]
                print('SERVER ERROR: '+message);

    def close(self):
        self.socket.close()

if __name__ == "__main__":
    root=tk.Tk()
    client = Client(root)
    client.mainloop()
