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
        self.timeout_amount = 1    # After 1 second, a timeout will occur

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

# Receiver packets reliably over UDP
class RDTReceiver:
    def __init__(self):
        self.ACK = 0    # Value of ACK to be sent with the message; Also acts as the FST variable
        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

    # Set the next ACK value to be used
    def increment_ACK(self):
        if self.ACK == 1:
            self.ACK = 0
        else:
            self.ACK = 1

    # Extract the sequence number from the message return as an int
    def get_sequence_number(self, byte_message)
        # The value extacted will be the ASCII representation of the number 0 or 1
        # '0' is 48 and '1' is 49, so subtract 48 to get the actual integer value
        return byte_message - 48

    def rdt_recv(self):
        #DO THIS:
        byte_message = received_packet  # Receive the UDP packet

        sequence_number = self.get_sequence_number(byte_message) # Extract the sequence number from the message
        print("Packet has sequence number: " + str(sequence_number))

        if sequence_number == self.ACK: # The expected sequence number was received;
            print("Sending ACK for " + str(self.ACK))
            self.udt_send(False)        # Send an ACK for the received packet
            self.increment_ACK()        # Change the ACK to the next expected sequence number
            return message              # Return the message to the application
        else:
            print("Re-sending ACK for " + str(self.ACK))
            self.udt_send(True)         # Resend the ACK of the previous packet
            return ""                   # Return nothing if the packet is corrupt or out of order

    # Construct the ACK packet and send the message with UDP
    # This functions is used by the receiver to send an ACK for the just received packet
    # If resend is true, an ACK for the previous packet is sent, otherwise, a new ACK for the current packet is sent
    def udt_send(self, resend):
        raw_message = ""    # Create the message to be sent

        # Place the appropriate ACK in the message, based on whether it is a retransmission or not
        if resend:
            self.increment_ACK()    # Get the previous ACK value
            message = str(self.ACK) + message
            self.increment_ACK()    # Restore the current ACK value
        else:   
            message = str(self.ACK) + message

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # DO THIS:
            # Send the packet over UDP
            return