#! /usr/bin/env python3
import threading
import socket
from pymavlink import mavutil
from queue import PriorityQueue
from PlaneController import PlaneController

def run(plane_address, server_address):
    mavutil.set_dialect("common")


    # Resources
    autopilot = mavutil.mavlink_connection(plane_address)

    plane_controller = PlaneController(autopilot, server_address)

    plane_controller.run()

if __name__ == "__main__":
    try:
        run('tcp:localhost:5763', "tbd")
    except KeyboardInterrupt:
        print("\nExiting...\n")