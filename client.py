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
        # Set up tk interface windows
        super().__init__(root)
        root.protocol("WM_DELETE_WINDOW",self.close)
        self.pack()
        self.serverip = ""
        self.username = ""
        self.serverport=""
        if len(sys.argv)==2:
            self.username=sys.argv[1]   # Get a default username from the command line
        f = open('client.conf')
        for line in f:                  # From the client.conf file, extract the default server ip and server port
            tokens=line.split()
            if tokens[0]=='DefaultServer':
                self.serverip=tokens[1]
            elif tokens[0]=='DefaultServerPort':
                self.serverport=int(tokens[1])
            elif tokens[0]=='DefaultUserName':
                self.username=int(tokens[1])
        f.close()
        self.createLoginWidgets()                   # Create the tk interface window
        self.socket=socket(AF_INET,SOCK_DGRAM)      # Open and bind the socket(s) need for the server to communicate
        self.rdtsender=RDTSender(self.socket)       # Objects used to send and receive
        self.rdtreceiver=RDTReceiver(self.socket)   # data reliably over the UDP connection
        self.running=False                          # Is the client program running and ready to send/receive?
        self.loggedin=False                         # Has a user logged in?
        self.filebuf=bytearray()                    # Create a buffer to use for file transfers

    # This is used to create the login interface with tk
    # This logic is mostly formating and not related to the actual chat protocol
    def createLoginWidgets(self):
        self.l1=tk.Label(self, text="Server IP:")   # Create aspects of the login screens (buttons, view, etc.)...
        self.l1.grid(row=0)
        self.l2=tk.Label(self, text="Server Port:")
        self.l2.grid(row=1)
        self.l3=tk.Label(self, text="Alias:")
        self.l3.grid(row=2)
        self.ip = tk.Entry(self)
        self.ip.insert(tk.END,self.serverip)        # Display the default server IP
        self.ip.grid(row=0, column=1)
        self.port=tk.Entry(self)
        self.port.insert(tk.END,self.serverport)    # Display the default server port
        self.port.grid(row=1,column=1)
        self.uname = tk.Entry(self)
        self.uname.insert(tk.END,self.username)     # Display the default username, if there is one
        self.uname.grid(row=2, column=1)
        self.connectBtn = tk.Button(self, text="Connect", fg="red",command=self.onConnect)
        self.connectBtn.grid(row=3,column=1)

    # When a connection is estbalished, remove the login window, create the chat window, and start the main loop
    # This mostly formating and not related to the actual chat protocol
    def onConnect(self):
        self.serverip = str(self.ip.get())      # Extract the user entered IP from the interface
        self.username = str(self.uname.get())   # Extract the username from the interface
        self.serverport=int(self.port.get())    # Extract the user entered port number from the interface
        self.username=self.username.replace(' ','-')    # Replace spaces in the user name with hyphins
        self.ip.destroy()                       # Remove the old interface...
        self.uname.destroy()
        self.l1.destroy()
        self.l2.destroy()
        self.connectBtn.destroy()
        self.l3.destroy()
        self.port.destroy()
        self.login(self.username)
        self.createMainWidgets()                # Create the main chat window
        self.start()                            # Start the main loop

    # Creates the main chat window, which displays messages and has buttons to send text or a transfer a file
    # This mostly formating and not related to the actual chat protocol
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

    # When the send text button is pressed, send the text user entered
    def onSendBtnPress(self):
        msg=self.textentry.get("1.0",tk.END)    # Extact and clear data from the box
        self.textentry.delete("1.0",tk.END)
        formatted_msg='MESSAGE '+self.username+' '+msg  # Craft the packet in our standard format
        self.sendbytes(formatted_msg.encode())          # Send the message

    # When the send file button is pressed, open a file explorer, select the file, and get the file path
    def onSendfileBtnPress(self):
        filetosend=filechooser.askopenfilename()    # Open the file explorer
        try:
            filesize=os.path.getsize(filetosend)    # Get filesize
            filename=ntpath.basename(filetosend).replace(' ','-')   # Get filename
            f=open(filetosend,'rb')
            bytes=f.read(filesize)
            self.sendfile(bytes,filename)           # Open file, read bytes, and send the file
        except Exception:
            dialog.showinfo('File Transfer','Error')

    # When the user logs in, send a notice to the server
    def login(self,username):
        formatted_msg='LOGIN '+username
        self.sendbytes(formatted_msg.encode())

    # When the user logs out, send a notice to the server
    def logout(self,username):
        formatted_msg='LOGOUT '+username
        self.sendbytes(formatted_msg.encode())

    # Main loop of the chat program; spawns a thread to handle the receiving
    def start(self):
        self.running=True
        self.recvThread=Thread(target=self.recvLoop)
        self.recvThread.daemon=True
        self.recvThread.start()

    # Thread handles the receiving of messages
    def recvLoop(self):
        while True:
            self.recvmessage()

    # Breaks up a file and send it in segments
    def sendfile(self,data,filename):
        for i in range(0,len(data),10000):
            lastsegment=(i+10000) >= len(data)
            if lastsegment==True:   # This segment is the final part of the file
                formatted_msg='FILE LAST '+self.username+' '+filename+' '   # Crafts the payload into our standard format
                msgbytes=formatted_msg.encode() # Convert the message to raw bytes
                bytestosend=b''.join([msgbytes,data[i:]])   # Add the file data bytes to the payload
                self.sendbytes(bytestosend)     # Send the bytes over the rdt protocol
            elif i==0:                          # First segment of the file
                formatted_msg='FILE FIRST '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)
            else:                               # This segment is a middle part of the file
                formatted_msg='FILE PART '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)

    # If the user wants to receive a file, request the file from the server
    def reqfile(self,fileid):
        formatted_msg='GET '+fileid+' '+self.username
        self.sendbytes(formatted_msg.encode())

    # The interface between the application and the application and the rdt protocol
    # This is called whenever a the client needs to send a message
    def sendbytes(self,bytes):
        self.rdtsender.rdt_send(bytes,(self.serverip, self.serverport))
        # self.socket.sendto(bytes,(self.serverip,self.serverport))

    # Handle the receiving of messages
    def recvmessage(self):
        bytes,addr=self.rdtreceiver.rdt_recv(65536)
        # bytes,addr=self.socket.recvfrom(65536)      # Receive packet payload

        print("Client: received rdt "+str(bytes))
        i=bytes.find(b' ',0)
        action=bytes[0:i].decode()  # Extract the action type of the raw received bytes
        if action == 'MESSAGE':     # A user sent a chat message, which is to be displayed
            lasti=i                 # These i and lasti values are used to segment the message for data extraction
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()  # Extract the username of the sender
            message=bytes[i+1:].decode()        # Extract the message
            if username == self.username:
                self.msgs.insert(tk.END,("You: "+message.replace('\n',' ')))    # Put "You" next to the message you sent and display the message
            else:
                self.msgs.insert(tk.END,(username+": "+message.replace('\n',' ')))  # Display the message
        elif action == 'ERROR':     # Error from server
            msg=bytes[i+1:].decode()
            print('SERVER ERROR: '+message);
        elif action == 'FILE?':     # Do you want to receive a file
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Extract the file name
            lasti=i
            i=bytes.find(b' ',lasti+1)          
            user_from=bytes[lasti+1:i].decode() # Extract the sender usernamae
            id=bytes[i+1:].decode()             # Extract the file id
            recvFile=dialog.askyesno('File Transfer','receive file '+filename+' from '+user_from+'?')   # Create a message box, ask the user if they want to receive the file
            if recvFile:
                self.reqfile(id)    # Get file from server if they do
        elif action == 'FILE':      # Recieve a file
            lasti=i
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()  # Get the file segment "part"
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Get the file name
            filedata=bytes[i+1:]                # Get the file data bytes

            if part=='FIRST':                   # First segment of the file
                self.filebuf=filedata
            else:
                self.filebuf=b''.join([self.filebuf,filedata]) #add on to file data
            if part=='LAST':                    # This segment is a middle part of the file
                saveloc=filechooser.asksaveasfilename(initialfile=filename) # Ask the save location
                try:
                    f=open(saveloc,'wb')    # Save the file
                    f.write(self.filebuf)
                    f.close()
                    dialog.showinfo('File Transfer','File saved to '+saveloc)
                except Exception:
                    dialog.showinfo('File Transfer','File not saved')
                self.filebuf=bytearray()

    # Close the sockets when the client is done
    def close(self):
        self.logout(self.username)
        self.socket.close()
        sys.exit(0)

if __name__ == "__main__":
    root=tk.Tk()
    client = Client(root)
    client.mainloop()
