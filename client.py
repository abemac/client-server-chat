from socket import *
import time
ip='127.0.0.1'
port=12000
server=(ip,port)
socket=socket(AF_INET,SOCK_DGRAM)
while True:
    message="Hi, I'm a client"
    socket.sendto(message.encode(),server)
    time.sleep(1)

socket.close()
