#! /usr/bin/env python3
# Define our data structures related to sending out jobs to the plane

from queue import Queue

class MessageJob():
    """Class to represent mavlink message we have to send"""
    def __init__(self, func, connection, *args):
        """Create the message object
        - func : Function to send the message. Ex: Mavlink.hearbeat_send
        - connection : The connection to send this mesage on
        - args : list of parameters to pass
        """
        self.func = func
        self.connection = connection
        self.args = args

    def send(self):
        """Send this job"""
        self.func(self.connection.mav, *self.args)
        