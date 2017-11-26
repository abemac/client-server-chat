from socket import *
socket = socket(AF_INET,SOCK_DGRAM)
socket.bind(('',12000))
while True:
    data, clientaddress=socket.recvfrom(2048)
    print(data.decode())
