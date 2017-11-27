import random
from socket import *
import time

# This file contains the code for the RDTSender and RDTReceiver classes.
# The RDTSender class implements the rdt3.0 sender protocol from the Kurose-Ross textbook.
# The RDTReceiver class implements the rdt2.2 receiver protocol from the Kurose-Ross textbook.
# These classes are used by the server and client to send messages reliably over a UDP connection.
# Because of the requirements of the lab, before sending the packet, these classes also simulate packet loss at random.
# The percent of packet loss is based on the percentage in the rdt.conf file.

# Send packet reliably over UDP
class RDTSender:

    # Initialize all the class variables
    def __init__(self):
        self.state = 0      # State of the FST
        self.timeout = 2    # After 2 seconds, a timeout will occur

        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

    def rdt_send(self, message):
        self.start_timer()

    def rdt_recv(self, message):
        return

    def udt_send(self, packet):

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            return

    def is_ACK(self):
        return

    def corrupt(self):
        return False

    # Timer used for detecting a timeout
    # Call everytime a rdt packet is sent
    def start_timer(self):
        self.start_time = time.time()

    # Timer used for detecting a timeout
    # Call everytime a rdt packet is received
    def stop_timer(self):
        self.end_time = time.time()

    # Returns a boolean; If the elapsed time after sending a packet is greater or equal to timeout,
    # then a timeout has occurred
    def is_timeout(self)
        return (self.end_time - self.start_time) >= self.timeout

    # def sender_loop(self):
    #     while True:
    #         if self.state == 0:
    #             return

    #         elif self.state == 1:
    #             return

    #         elif self.state == 2:
    #             return

    #         else:
    #             return

# Receiver packets reliably over UDP
class RDTReceiver:
    def __init__(self):
        self.state = 0  # State of the FST
        self.ACK = 0    # Value of ACK to be sent with the message
        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

    # Progresses the FST state to the next value
    def increment_state(self):
        if self.state == 1:
            self.state = 0
        else:
            self.state = 1

    # Set the next ACK value to be used
    def increment_ACK(self):
        if self.ACK == 1:
            self.ACK = 0
        else:
            self.ACK = 1

    # Extract the sequence number from the message return as an int
    def get_sequence_number(self, message)
        return int(message[0])

    def rdt_recv(self, received_packet):
        message = received_packet                           # Extract the message from the UDP packet
        sequence_number = self.get_sequence_number(message) # Extract the sequence number from the message

        if sequence_number == self.state and not corrupt(message)
            # The expected sequence number was received; change the state to the next expected sequence number
            self.increment_state()
            return message
        else:
            return ""   # Return nothing if the packet is corrupt or out of order

    # Construct the packet and send the message with UDP
    def udt_send(self):
        # Place the ACK in the message
        message = str(self.ACK) + message

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            return

    # Calculates the UDP checksum of the data Extracts the UDP checksum from the packet
    # Implement the RFC 1071 checksum method
    def corrupt(self, packet):
        # message = packet.message # Extract the message data from the packet

        # for ...   # Loop through the UDP packet and sum all the 16 bit segments
        checksum = 0

        if checksum == 0xFFFF:
            return False    # If the 16 bit checksum is all 1s, the packet is not corrupt
        else:
            return True     # The packet is corrupt
