from socket import *
from threading import Thread
import tkinter as tk
import tkinter.filedialog as filechooser
import tkinter.messagebox as dialog
from rdt import *
import os
import ntpath
import sys

# This file contains the code for the Client class. The class contains functions that create the user interface,
# allow a user to login or out, and manage the sending and receiving of files and messages. This program is multi-threaded
# to allow the simultaneous sending and receiving of data.

class Client(tk.Frame):
    def __init__(self,root):
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW",self.close)
        self.pack()
        self.serverip = ""
        self.username = ""
        self.serverport=""
        if len(sys.argv)==2:
            self.username=sys.argv[1]
        f = open('client.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='DefaultServer':
                self.serverip=tokens[1]
            elif tokens[0]=='DefaultServerPort':
                self.serverport=int(tokens[1])
            elif tokens[0]=='DefaultUserName':
                self.username=int(tokens[1])
        f.close()
        self.createLoginWidgets()
        self.socket=socket(AF_INET,SOCK_DGRAM)
        self.rdtsender=RDTSender(self.socket)
        self.rdtreceiver=RDTReceiver(self.socket)
        self.running=False      # Is the client program running and ready to send/receive?
        self.loggedin=False     # Has a user logged in?
        self.filebuf=bytearray()


    def createLoginWidgets(self):
        self.l1=tk.Label(self, text="Server IP:")
        self.l1.grid(row=0)
        self.l2=tk.Label(self, text="Server Port:")
        self.l2.grid(row=1)
        self.l3=tk.Label(self, text="Alias:")
        self.l3.grid(row=2)
        self.ip = tk.Entry(self)
        self.ip.insert(tk.END,self.serverip)
        self.ip.grid(row=0, column=1)
        self.port=tk.Entry(self)
        self.port.insert(tk.END,self.serverport)
        self.port.grid(row=1,column=1)
        self.uname = tk.Entry(self)
        self.uname.insert(tk.END,self.username)
        self.uname.grid(row=2, column=1)
        self.connectBtn = tk.Button(self, text="Connect", fg="red",command=self.onConnect)
        self.connectBtn.grid(row=3,column=1)

    def onConnect(self):
        self.serverip = str(self.ip.get())
        self.username = str(self.uname.get())
        self.serverport=int(self.port.get())
        self.username=self.username.replace(' ','-')
        self.ip.destroy()
        self.uname.destroy()
        self.l1.destroy()
        self.l2.destroy()
        self.connectBtn.destroy()
        self.l3.destroy()
        self.port.destroy()
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
        self.sendbytes(formatted_msg.encode())

    def onSendfileBtnPress(self):
        filetosend=filechooser.askopenfilename()
        try:
            filesize=os.path.getsize(filetosend)
            filename=ntpath.basename(filetosend).replace(' ','-')
            f=open(filetosend,'rb')
            bytes=f.read(filesize)
            self.sendfile(bytes,filename)
        except Exception:
            dialog.showinfo('File Transfer','Error')

    def login(self,username):
        formatted_msg='LOGIN '+username
        self.sendbytes(formatted_msg.encode())

    def logout(self,username):
        formatted_msg='LOGOUT '+username
        self.sendbytes(formatted_msg.encode())

    def start(self):
        self.running=True
        self.recvThread=Thread(target=self.recvLoop)
        self.recvThread.daemon=True
        self.recvThread.start()

    def recvLoop(self):
        while self.running==True:
            self.recvmessage()

    def sendfile(self,data,filename):
        for i in range(0,len(data),10000):
            lastsegment=(i+10000) >= len(data)
            if lastsegment==True:
                formatted_msg='FILE LAST '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:]])
                self.sendbytes(bytestosend)
            elif i==0:#First segment
                formatted_msg='FILE FIRST '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)
            else:
                formatted_msg='FILE PART '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)

    def reqfile(self,fileid):
        formatted_msg='GET '+fileid+' '+self.username
        self.sendbytes(formatted_msg.encode())

    def sendbytes(self,bytes):
        self.rdtsender.rdt_send(bytes,(self.serverip,self.serverport))
        #self.socket.sendto(bytes,(self.serverip,self.serverport))

    def recvmessage(self):
        bytes,addr=self.rdtreceiver.rdt_recv(65536)
        #bytes,addr=self.socket.recvfrom(65536)
        print("Client: received rdt "+str(bytes))
        i=bytes.find(b' ',0)
        action=bytes[0:i].decode()
        if action == 'MESSAGE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()
            message=bytes[i+1:].decode()
            if username == self.username:
                self.msgs.insert(tk.END,("You: "+message.replace('\n',' ')))
            else:
                self.msgs.insert(tk.END,(username+": "+message.replace('\n',' ')))
        elif action == 'ERROR':
            msg=bytes[i+1:].decode()
            print('SERVER ERROR: '+message);
        elif action == 'FILE?':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()
            lasti=i
            i=bytes.find(b' ',lasti+1)
            user_from=bytes[lasti+1:i].decode()
            id=bytes[i+1:].decode()
            recvFile=dialog.askyesno('File Transfer','receive file '+filename+' from '+user_from+'?')
            if recvFile:
                self.reqfile(id)
        elif action == 'FILE':
            lasti=i
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()
            filedata=bytes[i+1:]

            if part=='FIRST':
                self.filebuf=filedata
            else:
                self.filebuf=b''.join([self.filebuf,filedata]) #add on to file data
            if part=='LAST':
                saveloc=filechooser.asksaveasfilename(initialfile=filename)
                try:
                    f=open(saveloc,'wb')
                    f.write(self.filebuf)
                    f.close()
                    dialog.showinfo('File Transfer','File saved to '+saveloc)
                except Exception:
                    dialog.showinfo('File Transfer','File not saved')
                self.filebuf=bytearray()

    def close(self):
        self.logout(self.username)
        self.socket.close()
        sys.exit(0)

if __name__ == "__main__":
    root=tk.Tk()
    client = Client(root)
    client.mainloop()
