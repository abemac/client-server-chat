# client-server-chat  
Chat program in Python created by Abraham McIlvaine and Benjamin Steenkamer  
CISC450/CPEG419  
Programming Assignment- Project 2: Client-Server Chat Program  
11/27/17  

## Relevant Sub-Folder and Files:
**client/**  
    Folder that contains the client code file
**client/client.py**  
    Contains the code for the chat server  
**README.md**  
    This current file  
**rdt/**  
    Folder that contains the reliable data transfer code and configuration files  
**rdt/rdt.py**  
    Contains the code for reliable data transfer over the UDP connection; Used by both the client and server  
**rdt/rdt.conf**  
    Configuration settings used by rdt.py; Contains simulated packet loss percent  
**server/**  
    Folder that contains the server code and its related helper file(s)  
**server/server.py**  
    Contains the code for the chat server  
**server/util.py**  
    Helper functions used by server.py  

## Compilation instructions
This project is done in Python 3, so there is no "compiling" to be done.  
Make sure python 3 is installed on the system:  
    `sudo apt-get update`  
    `sudo apt-get install python3`  
Make sure the tkinter library for Python 2.7 is installed to run:  
    `sudo apt-get install python3-tk`  

## Configuration Files
**rdt/rdt.conf**  
This file contains 1 integer (and nothing else) that represents the percent chance a packet will be lost because of simulated packet loss.
The integer value must be between 0 and 100, inclusive, and it must be set before the client or server program is run.
For example, if the number in the file is 20, then there is a 20% chance that any one packet sent by the client or server will be dropped. This file already contains a sample value in it.  

## Running Instructions
**server/server.py**  
Start the server first:  
The server is a UDP server keeps track of all the currently logged in clients and sends messages/files to the users currently logged in.
To run the server, go to the main folder (AbrahamMcIlvaine-BenjaminSteenkamer) from the command line and type:  
    `python server/server.py`  
The server will display a print out in the console when it is running; No command line arguments are needed.
There should only be one instance of the server running at a times.  
**client/client.py**  
Now start the client:  
The client allows a person to log in with a username and send messages to the 1 or 2 other users on the server.
If there is at least 1 other user logged, in the client program can be used to send the user a text or binary file.
You can also receive a file from another user if you accept it. You then specify where the file is stored and what it is named.
To run a client, go to the main folder (AbrahamMcIlvaine-BenjaminSteenkamer) from the command line and type:  
   ` python client/client.py`  
The client will appear and you will be able to login; No command line arguments are needed.
If you want to add another, open up another command line and start another instance of the client.
The chat program only supports up to 3 simultaneous users, so only three client programs should be running at once.  
