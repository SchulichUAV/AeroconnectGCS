#! /usr/bin/env python3
import threading
from PlaneController import PlaneController
from MavlinkInterface import *

def run(id, plane_address, server_address):
    """Starts a loop that will handle the communication tasks required of the plane
    - plane_address : address of the PixHawk
    - sevrer_address : address of the server to make requests to
    """
    autopilot = mavutil.mavlink_connection(plane_address)
    plane_controller = \
        PlaneController(id, autopilot, server_address, debug=True)
    plane_controller.run()

if __name__ == "__main__":
    try:
        run(1,'tcp:localhost:5763', "http://204.48.28.172")
    except KeyboardInterrupt:
        print("\nExiting...\n")