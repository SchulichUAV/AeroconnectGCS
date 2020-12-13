# /usr/bin/env python3
import requests
import time
import threading
from urllib.parse import urljoin

from queue import PriorityQueue, Queue

from MavlinkInterface import *
from Messages import *
from PriorityLevels import *

class PlaneController():
    def __init__(self, id : int, autopilot, server_address, debug=True):
        """Initialize a PlaneController and start up it's threads
        - id : id of the plane in the database
        - autopilot : pymavlink autpilot connection
        - server_address : address of server we get jobs from
        """
        print("Setting up controller")
        # Attributes
        self.id = id
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

        self.register_with_server()
        self.init_data_streams() # Subscribe to location information
        self.handlers = self.register_handlers()

        # Status variables
        self.lat = None
        self.lon = None
    
        print("Setting up threads")
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self.send_command_thread = threading.Thread(target=self.send_commands_loop, daemon=True)
        self.read_command_thread = threading.Thread(target=self.read_commands_loop, daemon=True)
    
    def register_with_server(self):
        """Ask the server if a plane exists with our id. If it does not we will
        create it"""
        planes_url = urljoin(self.server_address,"planes/")
        r = requests.get(planes_url)
        if self.debug:
            print(r.url)
            print(r.text)
        if not self.id in [plane["id"] for plane in r.json()]:
            r = requests.post(planes_url, json={"id":self.id})
    
    def init_data_streams(self):
        """We need to send mav commands to initiate the datastreams we wants"""
        gps_request = StreamRequest(
            self.autopilot, 
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT,
            interval=1e6
        )
        self.command_queue.put(PrioritizedItem(stream_pri, gps_request))

    def register_handlers(self):
        """This tells us the default way to handle each message
        Return - dictionary of format <mesage id, handler>"""
        return {
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT : 
            self.handle_position,
        }

    def handle_position(self, msg):
        """Handle messages of type MAVLINK_MSG_ID_GLOBAL_POSITION_INT"""
        # For some reason message contains latitude and longitude times 1e7
        lat, lon = msg.lat/1e7, msg.lon/1e7
        if self.debug:
            print(f"Recorded position ({lat},{lon})")
        self.lat = lat
        self.lon = lon

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
                print(f"Send: {command}")
            command.send()
        
    def read_commands_loop(self):
        """Read mavlink messages from the plane and dispatch to the approriate 
        handler"""
        while True:
            msg = self.autopilot.recv_msg()
            if msg:
                if self.debug: print(f"Receive: {msg}")
                if msg.id in self.handlers:
                    handle_thread = threading.Thread(
                        target=self.handlers[msg.id],
                        args=(msg,)
                    )
                    handle_thread.start()
            time.sleep(0.1)

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
        self.send_command_thread.start()
        self.read_command_thread.start()

        while True:
            pass
