import random
from socket import *
import threading

# This file contains the code for the RDTSender and RDTReceiver classes.
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet lost is based on the percentage in the rdt.conf file (percentage is an int in [0, 100]).

# Send packet reliably over UDP
# This class sends data and receives ACKs
# The "states" of the sender are taken from Figure 3.15 in the Kurose-Ross text book
class RDTSender:
    # Initialize all the class variables
    def __init__(self,socket):
        self.state = 0              # The current position of the FST
        self.timeout_amount = 2     # After this many seconds, a timeout will occur
        self.timer = None           # The timer object used to detect timeouts

        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

        self.socket=socket;                     # Receive the socket information from the application
        print(self.socket)

    # State of the sender; Used to move the state from 0 -> 1 -> 2 -> 4 -> 0 ...
    def increment_state(self):
        if self.state < 3:
            self.state  = self.state + 1
        else:
            self.state = 0

    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data and reset the timer in case of another timeout
    def timeout(self,bytes,seqnum,addr):
        self.udt_send(bytes,seqnum,addr)

    # Called by the application to send a packet reliably over the UDP connection
    # The sender can only send a new message if has already received the previously sent packet
    def rdt_send(self,bytes,addr):
        if self.state == 0:         # "Waiting for call 0 above" state
            self.udt_send(bytes,0,addr)
            self.increment_state()  # Move into the "Wait for ACK 0" state
            self.timer=threading.Timer(self.timeout_amount, self.timeout,args=(bytes,0,addr))   
            self.timer.start()      # Start the timeout timer for detecting a timeout
            self.waitforACK(0)
            self.increment_state()  # Move into the "Waiting for call 1 above state"
        elif self.state == 2:       # The waiting for call 1 above state
            self.udt_send(bytes,1,addr)
            self.increment_state()  # Move in the "Wait for ACK 1" state
            self.timer=threading.Timer(self.timeout_amount, self.timeout,args=(bytes,1,addr))
            self.timer.start()
            self.waitforACK(1)
            self.increment_state()  # Move into the "Waiting for call 0 above" state

    # Receive a ACK message from the UDP connection
    def waitforACK(self,ack_number):
        bytes,addr=self.socket.recvfrom(2048)   # Get the UDP payload, which should contain the ACK
        sequence_number = int(bytes[0:1])       # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if self.is_ACK(bytes):
            if sequence_number == ack_number:   # The expected sequence number was received;
                self.timer.cancel()             # Stop the timeout timers
                print("Correct sequence number received")
                return
            else:
                print("Wrong sequence number")
                waitforAck(self,number)         # Continue to wait for the correct, in order ACK
        else:
            print("Packet is not an ACK (len=" + str(len(byte_message)) + ")")
            waitforAck(self,number)             # Continue to wait for the correct, in order ACK

    def udt_send(self, bytes,seq_number,addr):
        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            seq_byte=str(seq_number).encode()
            data=b''.join([seq_byte,bytes]) # Insert the sequence number at the front of the message
            self.socket.sendto(data,addr)

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def is_ACK(self, byte_message):
        if len(byte_message) == 1:
            return True
        else:
            return False

# Receiver packets reliably over UDP
# This class receives data and send ACKs
class RDTReceiver:
    def __init__(self,socket):
        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

        self.socket=socket
        self.state = 0  # The current position of the FST

    def rdt_recv(self,bufsize):
        bytes,addr=self.socket.recvfrom(bufsize)# Receive the UDP packet
        sequence_number = int(bytes[0:1])       # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if self.state==0:                       # "Wait for 0 from below" state
            if sequence_number==0:
                self.udt_send_ACK(0,addr)       # Send the ACK for the "0" packet
                self.state=1                    # Move to the "Wait for 1 from below" state
                return bytes,addr
            else:
                self.udt_send_ACK(1,addr)       # Resend the previous ACK
                return self.rdt_recv(bufsize)   # Continue to wait for the correct ACK
        elif self.state==1:                     # "Wait for 1 from below" state
            if sequence_number==1:
                self.udt_send_ACK(1,addr)       # Send the ACK for the "1" packet
                self.state=0
                return bytes,addr
            else:
                self.udt_send_ACK(0,addr)
                return self.rdt_recv(bufsize)

    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the received packet
    def udt_send_ACK(self, ack_number,addr):
        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            data=str(ack_number).encode()
            self.socket.sendto(data,addr)
