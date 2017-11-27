import random
from socket import *
import threading

# This file contains the code for the RDTSender and RDTReceiver classes.
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet loss is based on the percentage in the rdt.conf file.

# Send packet reliably over UDP
# The "states" of the sender are taken from Figure 3.15 in the Kurose-Ross text book
class RDTSender:
    # Initialize all the class variables
    def __init__(self,socket):

        self.state = 0              # The current position of the FST
        self.timeout_amount = 2     # After this many seconds, a timeout will occur
        self.timer = None # The timer object used to detect timeouts

        # Open rdt/rdt.conf and read in the packet_loss_percent value
        f = open('client.conf')
        for line in f:
            tokens=line.split()
            if tokens[0]=='PacketDropRate':
                self.packet_loss_percent=int(tokens[1])# Convert the string to an int
                                                       # Percent chance any one packet being sent is lost due to simulated packet loss


        self.socket=socket;
        print(self.socket)

    # State of the sender; Used to make the sender wait until the correct packet has been ACK
    def increment_state(self):
        if self.state < 3:
            self.state  = self.state + 1
        else:
            self.state = 0

    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data
    def timeout(self,bytes,seqnum,addr):
        self.udt_send(bytes,seqnum,addr)
        self.timer=threading.Timer(self.timeout_amount, self.timeout,args=(bytes,0,addr));
        self.timer.start()

    # Called by the application to send a packet reliably over the UDP connection
    # The sender can only send a new message if has already received the previously sent packet
    def rdt_send(self, bytes,addr):
        if self.state == 0:
            self.udt_send(bytes,0,addr)
            self.increment_state()  # Move in the "waiting" state
            self.timer=threading.Timer(self.timeout_amount, self.timeout,args=(bytes,0,addr));
            self.timer.start()
            self.waitforACK(0)
            self.increment_state()
        elif self.state == 2:
            self.udt_send(bytes,1,addr)
            self.increment_state()  # Move in the "waiting" state
            self.timer=threading.Timer(self.timeout_amount, self.timeout,args=(bytes,1,addr));
            self.timer.start()
            self.waitforACK(1)
            self.increment_state()

    # Receive a message from the UDP connection
    def waitforACK(self,ack_number):
        bytes,addr=self.socket.recvfrom(2048)
        sequence_number = int(bytes[0:1]) # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if self.is_ACK(bytes):
            if sequence_number == ack_number: # The expected sequence number was received;
                self.timer.cancel() #Stop the timeout timer
                print("Correct sequence number received")
                return
            else:
                print("Wrong sequence number")
                waitforAck(self,number)
        else:
            print("Packet is not an ACK (len=" + str(len(byte_message)) + ")")
            waitforAck(self,number)


    def udt_send(self, bytes,seq_number,addr):

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            seq_byte=str(seq_number).encode()
            data=b''.join([seq_byte,bytes])
            self.socket.sendto(data,addr)

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def is_ACK(self, byte_message):
        if len(byte_message) == 1:
            return True
        else:
            return False

# Receiver packets reliably over UDP
class RDTReceiver:
    def __init__(self,socket):

        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

        self.socket=socket
        self.state=0

    def rdt_recv(self,bufsize):

        bytes,addr=self.socket.recvfrom(bufsize)   # Receive the UDP packet
        sequence_number = int(bytes[0:1]) # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if self.state==0:
            if sequence_number==0:
                self.udt_send_ACK(0,addr)
                self.state=1
                return bytes,addr
            else:
                self.udt_send_ACK(1,addr)
                return self.rdt_recv(bufsize)
        elif self.state==1:
            if sequence_number==1:
                self.udt_send_ACK(1,addr)
                self.state=0
                return bytes,addr
            else:
                self.udt_send_ACK(0,addr)
                return self.rdt_recv(bufsize)

    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the just received packet
    # If resend is true, an ACK for the previous packet is sent, otherwise, a new ACK for the current packet is sent
    def udt_send_ACK(self, ack_number,addr):
        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            data=str(ack_number).encode()
            self.socket.sendto(data,addr)
