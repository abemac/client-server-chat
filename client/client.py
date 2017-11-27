from socket import *
from threading import Thread
import time
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
        self.running=False      # Is the client program running and ready to send/receive?
        self.loggedin=False     # Has a user logged in?

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
        formatted_msg='MESSAGE '+self.username+' '+msg
        self.sendmessage(formatted_msg)

    def onSendfileBtnPress(self):
        filetosend=filechooser.askopenfilename()
        try:
            filesize=os.path.getsize(filetosend)
            f=open(filetosend,'rb')
            bytes=f.read(filesize)
            self.sendfile(bytes)
        except FileNotFoundError:
            print("File not found")

    def login(self,username):
        formatted_msg='LOGIN '+username
        self.sendmessage(formatted_msg)

    def logout(self,username):
        formatted_msg='LOGOUT '+username
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
        formatted_msg='FILE '+self.username+','
        msgbytes=formatted_msg.encode()
        bytestosend=b''.join([msgbytes,data])
        print(bytestosend)
        self.socket.sendto(bytestosend,(self.serverip,self.serverport))

    def sendmessage(self,message):
        self.socket.sendto(message.encode(),(self.serverip,self.serverport))

    def recvmessage(self):
        bytes,addr=self.socket.recvfrom(2048)
        i=bytes.find(b' ',0)
        action=bytes[0:i].decode()
        if action == 'MESSAGE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()
            message=bytes[i+1:].decode()
            if username == self.username:
                self.msgs.insert(tk.END,("You: "+message.replace('\n','')))
            else:
                self.msgs.insert(tk.END,(username+": "+message.replace('\n','')))
        elif action == 'ERROR':
            msg=bytes[i+1:].decode()
            print('SERVER ERROR: '+message);


    def close(self):
        self.socket.close()

if __name__ == "__main__":
    root=tk.Tk()
    client = Client(root)
    client.mainloop()
