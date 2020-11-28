#! /usr/bin/env python3
import threading
from PlaneController import PlaneController
from pymavlink import mavutil

def run(plane_address, server_address):
    mavutil.set_dialect("common")
    autopilot = mavutil.mavlink_connection(plane_address)
    plane_controller = PlaneController(autopilot, server_address)
    plane_controller.run()

if __name__ == "__main__":
    try:
        run('tcp:localhost:5763', "tbd")
    except KeyboardInterrupt:
        print("\nExiting...\n")