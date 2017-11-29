# client-server-chat  
Chat program in Python created by Abraham McIlvaine and Benjamin Steenkamer  
CISC450/CPEG419, Fall 2017  
Programming Assignment- Project 2: Client-Server Chat Program  
11/27/17  

## Relevant and Files:
**client.conf**  
Contains the default server IP and port number the client will connect to  
**client.py**  
Contains the code for the chat server  
**rdt.conf**  
Configuration settings used by rdt.py; Contains simulated packet loss percent/rate  
**rdt.py**  
Contains the code for reliable data transfer over the UDP connection; Used by both the client and server   
**README.md**  
This current file  
**server.conf**  
Contains the default UDP port number the server opens up  
**server.py**  
Contains the code for the chat server  
**util.py**  
Helper functions used by server.py  

## Compilation instructions
This project is done in Python 3, so there is no "compiling" to be done.  
Make sure python 3 is installed on the system:  
    `sudo apt-get update`  
    `sudo apt-get install python3`  
Make sure the tkinter library for Python 3 is installed on the system:  
    `sudo apt-get install python3-tk`  

## Configuration Files
**client.conf**  
This file contains 2 lines. The first line starts with "DefaultServer " and is then followed by an IP address. This value will appear in the client interface "Server IP" box by
default when starting the client. From the client interface, this value can be changed, but every time the client is restarted, this value will be reloaded from the file.
The second line starts with "DefaultServerPort " and is followed by a port number. This number can also be changed from the client interface as needed, and will appear in the "Server Port" box by default.
For testing/use, the values provided in this file should be used to connect with the server, otherwise they must match the IP + port number the server is running on.  
An example of the file contents:  
`DefaultServer 127.0.0.1`  
`DefaultServerPort 12057`  
**rdt.conf**  
This file 1 line that starts with "PacketDropRate " and is followed by an integer. The integer represents the percent chance a packet will be lost because of simulated packet loss.
The integer value must be between 0 and 100, inclusive, and it must be set before the client or server program is run.
For example, if the integer in the file is 20, then there is a 20% chance that any one packet sent by the client or server will be dropped.  
An example of the file contents:  
`PacketDropRate 20`  
**server.conf**  
This file contains 1 line that starts with "Port " and is followed by a port number. This is the default port number the server will open a UDP connection on when it is started.
The client and server ports must match for the connection to work.  
An example of the file contents:  
`Port 12057`  
## Running Instructions
**server.py**  
Start the server first:  
The server is a UDP server that keeps track of all the currently logged in clients and sends messages/files to the users currently logged in.
To run the server, go to the main folder (AbrahamMcIlvaine-BenjaminSteenkamer) from the command line and type:  
`python3 server.py`  
The server will display a print out in the console when it is running; No command line arguments are needed when starting the server.
There should only be one instance of the server running at a time. When the server is running, type "help" in the console to get a list of command the server can do.
The avaliable commands are: users (show current logged in), files (show the currently buffered files), exit (stop the server and exit), help (list the available commands).  
**client.py**  
Now start the client:  
The client allows a person to log in with a username and send messages to the 1 or 2 other users on the server. It provides a tk interfaces with a login interface and chat room interface once they are logged in. If there is at least 1 other user logged in, the client program can be used to send the other user a text or binary file. If there are 3 users logged in, then one user can send the other 2 users the same file. You can also receive a file from another user if you accept it (a dialogue box will appear, asking you to accept or decline the file). A file explorer window will appear to specify where the file should be stored and what to name it if you accept it.  
To run a client instance, go to the main folder (AbrahamMcIlvaine-BenjaminSteenkamer) from a command line and type:  
`python3 client.py`  
The client interface window will appear and you will be able to login. The first 2 boxes (Server IP and Server Port) will be automatically filled with the values from client.conf. These values can now be changed or left as the current values, depending on what IP/port the server is currently running on (These default values should work without editing if you use them). The final box labeled "Alias" is where the user must enter there username. This name MUST be unique from other users already logged in!  
Another way to start the client program is with a single argument:  
`python3 client.py user_name`  
This is a faster way of filling in the "Alias" field when starting the client. The client program will start the same as before, but now the Alias field will be automatically filled with the username you entered as the argument. This is the only command line argument for this program.  
Once logged in, you will get a chat interface window. The top half shows messages sent by you (with the label "You" next to the message), and other people's messages will appear as they send them (with their usernames appearing next to them). You can send a message by typing in the text box on the bottom half of the interface and then click the "Send" button. You can also send files by clicking the "Send File" button. This will bring up a file explorer to find the file you want to send.  
If you want to add another user to the chat, open up another command line and start another instance of the client with one of the methods described above. The chat program only supports up to 3 simultaneous users, so only three client programs can be running at once.  
