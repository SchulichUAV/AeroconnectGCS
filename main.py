#! /usr/bin/env python3
import threading
import socket
from pymavlink import mavutil
from queue import PriorityQueue
from loops import *

def run(plane_address, server_address):
    mavutil.set_dialect("common")


    # Resources
    autopilot = mavutil.mavlink_connection(address)

    plane_controller = PlaneController(autopilot, server_address)

    plane_controller.run()

    # Queues are used to pass information in a threadsafe way from produces to consumers
    job_queue =  PriorityQueue() # Priority queues are threadsafe so we don't need the workaround
    command_queue = PriorityQueue() # List of commands and exit conditions. Exit conditions can be lambda function
    
    heartbeat_thread = threading.Thread(target=heartbeat_thread, args=(autopilot,mavlink_message_queue), daemon=True) # Send heartbeat to ardupilot
    get_jobs_thread = threading.Thread(target=heartbeat_thread, args=(autopilot,mavlink_message_queue), daemon=True) # Send heartbeat to ardupilot
    produce_commands_thread = 



if __name__ == "__main__":
    run('tcp:localhost:5763', "tbd")