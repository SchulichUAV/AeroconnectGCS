# /usr/bin/env python3
import time
import threading

from queue import PriorityQueue, Queue

from Messages import *
from PriorityLevels import *

class PlaneController():
    def __init__(self, autopilot, server_address, debug=True):
        """Initialize a PlaneController and start up it's threads
        - autopilot : pymavlink autpilot connection
        - server_address : address of server we get jobs from
        """
        print("Setting up controller")
        # Attributes
        self.autopilot = autopilot
        self.server_address = server_address
        self.debug = debug

        # Queues are used to pass information in a threadsafe way from produces to consumers
        self.job_queue = PriorityQueue() # Priority queues are threadsafe so we don't need the workaround
        self.command_exit_queue = PriorityQueue() # List of commands and exit conditions. Exit conditions can be lambda function
        self.received_message_queue = Queue() # Messages received from the plane
        self.send_message_queue = Queue()
        self.server_jobs_queue = Queue() # List of jobs received from server
        self.acks = Queue() # Queue of acks to be fulfilled?

        self.command_queue = PriorityQueue()
        
        self.current_command = None
        self.next_command_condition = None # Are we ready for the next command?
        self.current_job = None
        self.next_job_condition = None # Are we ready for the next job?

        print("Setting up threads")
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self.command_thread = threading.Thread(target=self.send_commands_loop, daemon=True)
    
    def heartbeat_loop(self):
        """Send a heartbeat to the autopilot once every second"""
        while True:
            # The MAVLink class will be implicitly imported
            self.command_queue.put(PrioritizedItem(heartbeat_pri, Heartbeat(self.autopilot)) )
            time.sleep(1)

    def send_commands_loop(self):
        while True:
            """Get commands from the queue and send them to the plane"""
            command = self.command_queue.get().item
            if self.debug:
                print(command)
            command.send()

    def run(self):
        """Run all the threads and then go into an infinite loop"""
        # Pipeline for sending jobs out is

        # get_new_jobs (polls the server)
        # handle_server_responses (actual logic to put them in the right queue)
        # parse_jobs : parses job responses
        # check_command_done : check if the exit condition is met and if so get current_cmd from the command queue
        #   If the whole job is done we can get a new job

        # In parallel we have
        # get_plane_stats (poll planes for params or whatever)
        # post_plane_stats (send plane stats to the server)

        # And
        # send_plane_commands : read commands from the list and send them consume an ack if required
        # parse_commands : parsed the received commands queue for stats about the plane
        # handle_plane_commands : parse messages received from plane        
        # Heartbeat - this is just a normal heartbeat function

        print("Running")
        self.heartbeat_thread.start()
        self.command_thread.start()

        while True:
            pass

        pass
