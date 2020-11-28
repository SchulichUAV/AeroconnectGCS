#! /usr/bin/env python3
# Utility classes for commonly used messages

from Jobs import MessageJob
from pymavlink import mavutil
mavutil.set_dialect("common")

# Provides access to teh MAVLink functions to send messages
mav = mavutil.mavlink.MAVLink

class Heartbeat(MessageJob):
    def __init__(self, connection):
        super().__init__(mav.heartbeat_send, connection, 6, 8, 102, 0, 4, 3)
    def __repr__(self):
        return "Heartbeat"