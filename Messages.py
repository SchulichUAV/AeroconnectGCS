#! /usr/bin/env python3
# Utility classes for commonly used messages

from Jobs import MessageJob
from MavlinkInterface import mav, mavutil
from Waypoint import Waypoint

class WaitJob():
    """Placeholder job that doesn't actually do anything"""
    def __init__(self):
        self.send = None

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

class SetMode(MessageJob):
    """Set mode for the vehicle"""
    def __init__(self, connection, mode):
        super().__init__(
            mav.command_long_send, connection, 0, 0,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 
            mode, 0, 0 ,0 ,0, 0
        )
        self.mode = mode
    def __repr__(self):
        return f"Set mode {self.mode}"

class Arm(MessageJob):
    """Arm the vehicle for flight"""
    def __init__(self, connection):
        super().__init__(
            mav.command_long_send, connection, 0, 0,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            # The 1 here indicates ARM. 0 would mean disarm
            0, 1, 0, 0, 0, 0, 0, 0
        )
    def __repr__(self):
        return "Arm"

class Takeoff(MessageJob):
    """Take off and fly to a certain height"""
    def __init__(self, connection, altitude):
        super().__init__(
            mav.command_long_send, connection, 0,
            mavutil.mavlink.MAV_COMP_ID_SYSTEM_CONTROL, 
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, 0,
            altitude
        )
        self.altitude = altitude
    def __repr__(self):
        return f"Take off {self.altitude}"

class FlyTo(MessageJob):
    """Presuming we have taken off fly to this location and altitude"""
    def __init__(self, connection, waypoint : Waypoint, altitude):
        super().__init__(
            mav.mission_item_int_send, connection, 0, 0, 0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT, 
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 2, 0, 0, 0, 0, 0, 
            int(waypoint.lat*1e7), int(waypoint.lon*1e7), 
            # Multiply by 1.0e7 because ardupilot expects an int
            altitude
        )
        self.altitude = altitude
        self.waypoint = waypoint
    def lat(self):
        return self.waypoint.lat
    def lon(self):
        return self.waypoint.lon
    def __repr__(self):
        return f"Fly to {self.lat()} {self.lon()} at {self.altitude}"
