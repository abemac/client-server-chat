from socket import *
from threading import Thread,Lock
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
        self.root = root
        self.winfo_toplevel().title("Chat Client")
        self.pack()
        self.serverip = ""  # The IP address of the chat server the client is connecting to
        self.username = ""  # The username the chat client will login with
        self.serverport=""  # The port number of the chat server the client is connecting to
        if len(sys.argv)==2:
            self.username=sys.argv[1]   # Use the user name from the command line as the default if provided one
        f = open('client.conf')         # Open the client.conf file and get the default values
        for line in f:
            tokens=line.split()
            if tokens[0]=='DefaultServer':
                self.serverip=tokens[1]             # Get the default server IP
            elif tokens[0]=='DefaultServerPort':
                self.serverport=int(tokens[1])      # Get the default server port
            elif tokens[0]=='DefaultUserName':
                self.username=int(tokens[1])        # Get a default username
        f.close()
        self.createLoginWidgets()                   # Create the login interface
        self.socket=socket(AF_INET,SOCK_DGRAM)      # Create the socket the client will communicate over
        self.rdt=RDTManager(self.socket)            # This object will handle the sending and receiving of messages over the unreliable UDP connection
                                                    # It acts as the interface between the network and the application

        self.running=False          # Is the client program running and ready to send/receive?
        self.loggedin=False         # Has a user logged in?
        self.filebuf=bytearray()    # Buffer for storing a received file

    # Creates the login interface using tk. Most of this logic is formatting and not related to the chat protocol
    def createLoginWidgets(self):
        self.l1=tk.Label(self, text="Server IP:")   # Create text and arrange window with labels and text boxes
        self.l1.grid(row=0)
        self.l2=tk.Label(self, text="Server Port:")
        self.l2.grid(row=1)
        self.l3=tk.Label(self, text="Alias:")
        self.l3.grid(row=2)
        self.ip = tk.Entry(self)
        self.ip.insert(tk.END,self.serverip)        # Inserts the default IP into the text box
        self.ip.grid(row=0, column=1)
        self.port=tk.Entry(self)
        self.port.insert(tk.END,self.serverport)    # Inserts the default server into the text box
        self.port.grid(row=1,column=1)
        self.uname = tk.Entry(self)
        self.uname.insert(tk.END,self.username)     # Inserts the default username into the text box
        self.uname.grid(row=2, column=1)
        self.connectBtn = tk.Button(self, text="Connect", fg="red",command=self.onConnect)  # Create Connect button
        self.connectBtn.grid(row=3,column=1)

        self.connectBtn.bind('<Return>',self.onEnterPressLogin)
        self.uname.bind('<Return>',self.onEnterPressLogin)
        self.port.bind('<Return>',self.onEnterPressLogin)
        self.ip.bind('<Return>',self.onEnterPressLogin)
        self.uname.focus()

    def onEnterPressLogin(self,event):
        self.onConnect()

    # This function is called when the "Connect button is created"
    def onConnect(self):
        self.serverip = str(self.ip.get())
        self.username = str(self.uname.get())
        self.serverport=int(self.port.get())
        self.username=self.username.replace(' ','-')
        self.winfo_toplevel().title("Chat Client - "+self.username)
        self.ip.destroy()
        self.uname.destroy()
        self.l1.destroy()
        self.l2.destroy()
        self.connectBtn.destroy()
        self.l3.destroy()
        self.port.destroy()
        self.login(self.username)               # Send a message to the server to tell ii this user logged in
        self.createMainWidgets()                # Create the main chat interface
        self.start()                            # Start the main loop of the program

    #Creates the chat interface using tk. Most of this logic is formatting and not related to the chat protocol
    def createMainWidgets(self):
        self.sendfilebtn = tk.Button(self, text="SEND FILE", fg="red",command=self.onSendfileBtnPress)  # Create the send text button
        self.sendfilebtn.pack(side="bottom")

        self.sendbtn = tk.Button(self, text="SEND", fg="red",command=self.onSendBtnPress)   # Create the send file button
        self.sendbtn.pack(side="bottom")

        self.textentry=tk.Text(self,height=3,width=40)      # View where chat messages will be entered by the user
        self.textentry.pack(side="bottom")

        self.scrollbar=tk.Scrollbar(self)                   # Scroll bar for viewing older sent message
        self.scrollbar.pack(side=tk.RIGHT,fill=tk.Y)
        self.msgs=tk.Listbox(self,yscrollcommand=self.scrollbar.set,width=40)   # Main view where received messages will be displayed.

        self.msgs.pack(side=tk.LEFT,fill=tk.BOTH)
        self.scrollbar.config(command=self.msgs.yview)

        self.winfo_toplevel().bind('<Return>',self.onEnterPressSend)
        self.textentry.focus()

    # Runs when the user clicks the SEND button for text
    def onEnterPressSend(self,event):
        if self.textentry == self.root.focus_get():
            self.onSendBtnPress()
    # Runs when the user clicks the SEND button for text
    def onSendBtnPress(self):
        msg=self.textentry.get("1.0",tk.END)            # Extract message the user entered in the text box
        self.textentry.delete("1.0",tk.END)             # Clear the message box
        formatted_msg='MESSAGE '+self.username+' '+msg  # Craft the packet with a flag and the data
        self.sendbytes(formatted_msg.encode())          # Send the data as raw bytes

    # Runs when the user clicks the SEND button for text
    def onSendfileBtnPress(self):
        if filetosend != '' and filetosend!=():
            filetosend=filechooser.askopenfilename()    # Open the file explorer so the user can select a file
            try:
                filesize=os.path.getsize(filetosend)    # Get the size of the selected file
                filename=ntpath.basename(filetosend).replace(' ','-')   # Replace spaces in a user name with hyphens
                f=open(filetosend,'rb')         # Open the selected file
                bytes=f.read(filesize)          # Get the raw file bytes
                self.sendfile(bytes,filename)   # Send the file
            except Exception as e:
                #print(repr(e))
                dialog.showinfo('File Transfer',str(e))

    # Sends a message to server that notifies the server that a new user logged in
    def login(self,username):
        formatted_msg='LOGIN '+username         # Craft the packet with a identify flag and add the data on the end
        self.sendbytes(formatted_msg.encode())  # Send the packet as raw bytes
        self.loggedin=True
    # Sends a message to server that notifies the server that a user logged out
    def logout(self,username):
        formatted_msg='LOGOUT '+username        # Craft the packet with a identify flag and add the data on the end
        self.sendbytes(formatted_msg.encode())
        self.loggedin=False

    # The main look of the client. Starts the the thread that handles the receiving of message
    def start(self):
        self.running=True   # Client is now connected and running
        self.recvThread=Thread(target=self.recvLoop)    # Create the thread that handles the receiving of data
        self.recvThread.daemon=True # Thread will end when main thread ends
        self.recvThread.start()     # Launch the thread

    # Work loop of the recvThread. It is always trying to receive new messages
    def recvLoop(self):
        while True:
            self.recvmessage()

    # Segments a file into 10000 byte chunks and send them to the server
    def sendfile(self,data,filename):
        for i in range(0,len(data),10000):
            lastsegment=(i+10000) >= len(data)
            if lastsegment==True:       # If this packet is the final segment of the file
                formatted_msg='FILE LAST '+self.username+' '+filename+' '   # Craft the packet and mark the data as the final piece of the file
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:]])   # Join the file data with the rest of the packet
                self.sendbytes(bytestosend)                 # Send the packet
            elif i==0:                  # If this packet is the first segment of the file
                formatted_msg='FILE FIRST '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)
            else:                       # If this packet is middle segment of the file
                formatted_msg='FILE PART '+self.username+' '+filename+' '
                msgbytes=formatted_msg.encode()
                bytestosend=b''.join([msgbytes,data[i:i+10000]])
                self.sendbytes(bytestosend)

    # When the user accepts a file to be received, as the server to send that file
    def reqfile(self,fileid):
        formatted_msg='GET '+fileid+' '+self.username
        self.sendbytes(formatted_msg.encode())

    # Sends the bytes of packet to the lower rdt level, which will handle the actual sending
    def sendbytes(self,bytes):
        self.rdt.send(bytes,(self.serverip,self.serverport))
        #self.socket.sendto(bytes,(self.serverip,self.serverport))

    # Received a message by calling the lower rdt level and process its data
    def recvmessage(self):
        bytes,addr=self.rdt.recv()  # Get the packet from the lower level
        #bytes,addr=self.socket.recvfrom(65536)
        i=bytes.find(b' ',0)        # These i and lasti values are used to segment the message for data extraction
        action=bytes[0:i].decode()  # Extract the flag at the start of the packet
        if action == 'MESSAGE':     # If the received message is chat message
            lasti=i
            i=bytes.find(b' ',lasti+1)
            username=bytes[lasti+1:i].decode()  # Get the username of the person who sent the message
            message=bytes[i+1:].decode()
            if username == self.username:       # If you sent this message...
                self.msgs.insert(tk.END,("You: "+message.replace('\n',' ')))    # Display "You" next to your message
            else:
                self.msgs.insert(tk.END,(username+": "+message.replace('\n',' ')))  # Other wise display the actual user name
            self.msgs.see(tk.END) #scroll message view to end
        elif action == 'ERROR':     # If the server had an error
            msg=bytes[i+1:].decode()
            print('SERVER ERROR: '+message);    # Display the error
        elif action == 'FILE?':     # A file request
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Extact the file name
            lasti=i
            i=bytes.find(b' ',lasti+1)
            user_from=bytes[lasti+1:i].decode() # Extact the user who send it
            id=bytes[i+1:].decode()
            recvFile=dialog.askyesno('File Transfer','receive file '+filename+' from '+user_from+'?')   # Ask the user if they want to accept this file
            if recvFile:
                self.reqfile(id)    # If they do want this file, ask the server for it
        elif action == 'FILE':      # The packet contains part of a file
            lasti=i
            i=bytes.find(b' ',lasti+1)
            part=bytes[lasti+1:i].decode()  # Extract which segment this packet contains (first, middle, last)
            lasti=i
            i=bytes.find(b' ',lasti+1)
            filename=bytes[lasti+1:i].decode()  # Get the file name
            filedata=bytes[i+1:]                # Get the raw file bytes

            if part=='FIRST':       # If this is first segment, add the data to the buffer
                self.filebuf=filedata
            else:
                self.filebuf=b''.join([self.filebuf,filedata]) # Add on to file data already received
            if part=='LAST':    # If this is the last segment of the file
                saveloc=filechooser.asksaveasfilename(initialfile=filename) # ASk the user where to save the file
                try:
                    f=open(saveloc,'wb')    # Create the file
                    f.write(self.filebuf)   # Write the data to the fie
                    f.close()
                    dialog.showinfo('File Transfer','File saved to '+saveloc)   # Tell the user the transfer was successful
                except Exception:
                    dialog.showinfo('File Transfer','File not saved')           # Tell the user the transfer was not successful
                self.filebuf=bytearray()

    # When the client is exited
    def close(self):
        self.logout(self.username)  # Tell the server the user is logging out
        self.socket.close()         # Close the socket
        sys.exit(0)

# The starting point of the program. Creates the client object and starts it
if __name__ == "__main__":
    root=tk.Tk()
    client = Client(root)
    client.mainloop()
