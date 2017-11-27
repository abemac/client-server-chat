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
    def __init__(self):
        self.sequence_number = 0    # The sequence number of the packet
        self.state = 0              # The current position of the FST
        self.timeout_amount = 2     # After this many seconds, a timeout will occur
        self.timer = threading.Timer(self.timeout_amount, self.timeout) # The timer object used to detect timeouts

        # Open rdt/rdt.conf and read in the packet_loss_percent value
        with open("rdt.conf") as file:
            line = file.readline()

        line = line.rstrip()                    # Strip the '\n' character
        self.packet_loss_percent = int(line)    # Convert the string to an int
                                                # Percent chance any one packet being sent is lost due to simulated packet loss

    # State of the sender; Used to make the sender wait until the correct packet has been ACK
    def increment_state(self):
        if self.state < 3:
            self.state  = self.state + 1
        else:
            self.state = 0

    # Set the next sequence value to be used
    def increment_sequence_number(self):
        if self.sequence_number == 1:
            self.sequence_number = 0
        else:
            self.sequence_number = 1

    # This function is called then the timer object times out
    # It is used to resend the lost data/dropped data
    def timeout():
        #DO THIS:
        a = 1

    # Called by the application to send a packet reliably over the UDP connection
    # The sender can only send a new message if has already received the previously sent packet
    def rdt_send(self, message):
        if self.state == 0 or self.state == 2:
            self.udt_send(message)
            self.increment_state()  # Move in the "waiting" state
            self.timer.start()

    # Extract the sequence number from the message return as an int
    def get_sequence_number(self, byte_message):
        # The value extacted will be the ASCII representation of the number 0 or 1
        # '0' is 48 and '1' is 49, so subtract 48 to get the actual integer value
        return byte_message - 48

    # Receive a message from the UDP connection
    def rdt_recv(self):
        #DO THIS:
        byte_message = 0  # Receive the UDP packet

        sequence_number = self.get_sequence_number(byte_message) # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if sequence_number == self.sequence_number: # The expected sequence number was received;
            if self.is_ACK(byte_message):
                self.timer.cancel() #Stop the timeout timer
                print("Correct sequence number received")
                self.increment_sequence_number()        # Change the ACK to the next expected sequence number
                return byte_message                     # Return the message to the application
            else:
                print("Packet is not an ACK (len=" + str(len(byte_message)) + ")")
                return ""
        else:
            print("Wrong sequence number")
            return ""                   # Return nothing if the packet is corrupt or out of order

    def udt_send(self, message):

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # send the packet over UDP
            return

    # Checks if the received message is an ACK message.
    # An ACK message will only have 1 value in it, i.e. have a length of 1
    def is_ACK(self, byte_message):
        if len(byte_message) == 1:
            return True
        else:
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
    def get_sequence_number(self, byte_message):
        # The value extacted will be the ASCII representation of the number 0 or 1
        # '0' is 48 and '1' is 49, so subtract 48 to get the actual integer value
        return byte_message - 48

    def rdt_recv(self):
        #DO THIS:
        byte_message = 0    # Receive the UDP packet

        sequence_number = self.get_sequence_number(byte_message) # Extract the sequence number from the message
        print("Received packet has sequence number: " + str(sequence_number))

        if sequence_number == self.ACK: # The expected sequence number was received;
            print("Sending ACK for " + str(self.ACK))
            self.udt_send(False)        # Send an ACK for the received packet
            self.increment_ACK()        # Change the ACK to the next expected sequence number
            return byte_message         # Return the message to the application
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
            raw_message = str(self.ACK) + raw_message
            self.increment_ACK()    # Restore the current ACK value
        else:   
            raw_message = str(self.ACK) + raw_message

        # Simulate packet loss
        if random.randint(1, 100) <= self.packet_loss_percent:
            return     # Packet is lost, don't actually send the packet
        else:
            # DO THIS:
            # Send the packet over UDP
            return