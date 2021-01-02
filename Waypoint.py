#! /usr/bin/env python3

class Waypoint():
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon
    def get_lat(self):
        return self.lat
    def get_lon(self):
        return self.lon

class WaypointStage():
    """Step on the way to a waypoint"""
    def __init__(self, command, exit_condition=lambda:True):
        """
        command : MavLink command to send when we start this waypoint
        exit_condition : function to tell when to move to the next stage 
        """
        self.command = command
        self.exit_condition = exit_condition
    def done(self):
        return self.exit_condition()
    def get_command(self):
        return self.command
