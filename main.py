#! /usr/bin/env python3
import threading
from PlaneController import PlaneController
from MavlinkInterface import *

def run(plane_address, server_address):
    """Starts a loop that will handle the communication tasks required of the plane
    - plane_address : address of the PixHawk
    - sevrer_address : address of the server to make requests to
    """
    autopilot = mavutil.mavlink_connection(plane_address)
    plane_controller = PlaneController(autopilot, server_address)
    plane_controller.run()

if __name__ == "__main__":
    try:
        run('tcp:localhost:5763', "tbd")
    except KeyboardInterrupt:
        print("\nExiting...\n")