#! /usr/bin/env python3
# Utility classes for commonly used messages

from Jobs import MessageJob
from MavlinkInterface import mav, mavutil

class Heartbeat(MessageJob):
    def __init__(self, connection):
        super().__init__(mav.heartbeat_send, connection, 6, 8, 102, 0, 4, 3)
    def __repr__(self):
        return "Heartbeat"

class StreamRequest(MessageJob):
    """Request a mesage to be regularly sent from the autopilot."""
    def __init__(self, connection, message, interval : int):
        """
        connection - connection to send request to
        message - id of the message to request
        interval - interval between messages in microseconds (us)
        """
        super().__init__(
            mav.command_long_send, connection, 0, 0, 
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0, 
            message, interval, 0, 0, 0, 0, 0
            )
        self.message = message
    def __repr__(self):
        return f"Request {self.message}"      
