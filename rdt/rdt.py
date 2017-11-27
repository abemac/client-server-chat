from socket import *
import time

# This file contains the code for the RDTSender and RDTReceiver classes. 
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by both the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet loss is based on the percentage in the rdt.conf file.

class RDTSender:
    def __init__(self):
        self.state = 0      # State of the FST
        self.timeout = 3    # After 3 seconds, a timeout will occur   

    def rdt_send(self, message):
        self.start_timer()

    def rdt_recv(self, message):

    def udt_send(self, packet):

    def is_ACK(self):

    def corrupt(self):

    # Timer used for detecting a timeout
    # Call everytime a rdt packet is sent
    def start_timer(self):
        self.start_time = time.time()

    # Timer used for detecting a timeout
    # Call everytime a rdt packet is received
    def stop_timer(self):
        self.end_time = time.time()

    def sender_loop(self):
        while True:
            if state == 0:

            elif state == 1:

            elif state == 2:

            else:


# This class implements the rdt2.2 receiver protocol from the book
# It is used by both the server and client to send receive reliably over a UDP connection
class RDTReceiver:
    def __init__(self):
        self.state = 0

    def state_machine(self):


    def rdt_recv(self, received_packet):
        sequence_number = received_packet.sequence_number
        if not corrupt(received_packet) and sequence_number == state:
            return received_packet.message
        else:

    # Construct the packet and send the message with UDP
    def udt_send(self, message):        
        # Place the ACK in the message
        # send the packet over UDP

    # Calculates the UDP checksum of the data Extracts the UDP checksum from the packet
    # Implement the RFC 1071 checksum method
    def corrupt(self, packet):
        # message = packet.message # Extract the message data from the packet

        # for ...   # Loop through the UDP packet and sum all the 16 bit segments
            # checksum = 

        if checksum == 0xFFFF:
            return False    # If the 16 bit checksum is all 1s, the packet is not corrupt
        else:
            return True     # The packet is corrupt

    
