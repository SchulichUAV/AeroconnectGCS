#! /usr/bin/env python3
# Commonly used messages

from Jobs import Message

class Message():
    def __init__(self, connection, *args):
        self.connection = connection
        self.args = args

def heartbeat_message(autopilot):
    return Message(autopilot.mav.heartbeat_send, (6, 8, 102, 0, 4, 3))
