# /usr/bin/env python3
import Modes
import requests
import time
import threading
from urllib.parse import urljoin

from queue import PriorityQueue, Queue
from haversine import haversine, Unit

from MavlinkInterface import *
from Messages import *
from Modes import *
from PriorityLevels import *
from Waypoint import *

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

        self.register_with_server()
        self.init_data_streams() # Subscribe to location information
        self.handlers = self.register_handlers()

        # Status variables
        self.lat = None
        self.lon = None
        self.relative_alt = 0
        self.waypoint_reached = False
        self.armed = False
        # In an actual system we would have a button or something
        self.loaded = True
        self.flightstage = None # Same as the "landed" attribute in ardupilot

        # Waypoint completion variables
        self.waypoints = Queue() # List of waypoints to visit
        self.next_waypoint = None
        self.instructions = Queue() # Stages of current waypoint
        self.current_stage = None
    
        print("Setting up threads")
        self.heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        self.send_command_thread = threading.Thread(target=self.send_commands_loop, daemon=True)
        self.read_command_thread = threading.Thread(target=self.read_commands_loop, daemon=True)
        self.update_waypoint_thread = threading.Thread(target=self.update_waypoint_loop, daemon=True)

    # Utils

    def distance_to(self, waypoint):
        """
        Return the distance to the waypoint in meters using the haversine
        formula.
        """
        current_loc = (self.lat, self.lon)
        waypoint_loc = (waypoint.get_lat(), waypoint.get_lon())
        return haversine(current_loc, waypoint_loc, unit=Unit.METERS)

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
        mission_reached = StreamRequest(
            self.autopilot,
            mavutil.mavlink.MAVLINK_MSG_ID_MISSION_ITEM_REACHED,
            interval=1e6
        )
        extended_sys_request = StreamRequest(
            self.autopilot,
            mavutil.mavlink.MAVLINK_MSG_ID_EXTENDED_SYS_STATE,
            interval=1e6
        )
        self.command_queue.put(
            PrioritizedItem(stream_pri, gps_request)
        )
        self.command_queue.put( 
            PrioritizedItem(stream_pri, mission_reached)
        )
        self.command_queue.put(
            PrioritizedItem(stream_pri, extended_sys_request)
        )

    def register_handlers(self):
        """This tells us the default way to handle each message
        Return - dictionary of format <mesage id, handler>"""
        return {
            mavutil.mavlink.MAVLINK_MSG_ID_GLOBAL_POSITION_INT : 
            self.handle_position,
            mavutil.mavlink.MAVLINK_MSG_ID_MISSION_ITEM_REACHED :
            self.handle_waypoint_reached,
            mavutil.mavlink.MAVLINK_MSG_ID_HEARTBEAT :
            self.handle_heartbeat,
            mavutil.mavlink.MAVLINK_MSG_ID_EXTENDED_SYS_STATE :
            self.handle_extended_sys_state,
        }

    def handle_position(self, msg):
        """Handle messages of type MAVLINK_MSG_ID_GLOBAL_POSITION_INT"""
        # For some reason positional values in the message are multiplied by 1e7
        lat, lon, relative_alt = msg.lat/1e7, msg.lon/1e7, msg.relative_alt/1e3
        if self.debug:
            print(f"Recorded position ({lat},{lon})")
        self.lat = lat
        self.lon = lon
        self.relative_alt = relative_alt

    def handle_waypoint_reached(self, msg):
        """Handle MISSION_ITEM_REACHED"""
        self.waypoint_reached = True

    def handle_heartbeat(self, msg):
        # Heartbeat contains mode information
        if msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
            self.armed = True
        else:
            self.armed = False
    
    def handle_extended_sys_state(self, msg):
        self.flightstage = msg.landed_state

    def get_new_instruction(self):
        """Moves the mission along"""
        if self.instructions.empty():
            if self.debug: print("Getting waypoint")
            self.next_waypoint = self.waypoints.get()
            if self.debug: print("Got waypoint")
            self.waypoint_reached = False
            new_instructions = \
                self.generate_waypoint_instructions(self.next_waypoint)
            for instruction in new_instructions:
                self.instructions.put(instruction)
        else:
            self.current_stage = self.instructions.get()
            command = self.current_stage.get_command()
            # Some commands don't send anything e.g. wait
            if command.send:
                self.command_queue.put(PrioritizedItem(nav_pri, command))

    def generate_waypoint_instructions(self, waypoint : Waypoint):
        """Generates instructions to go to a certain waypoint"""
        return [
            WaypointStage(
                WaitJob(), lambda : self.loaded
            ),
            WaypointStage(
                SetMode(self.autopilot, Modes.GUIDED)
            ),
            WaypointStage(
                Arm(self.autopilot), lambda : self.armed
            ),
            WaypointStage(
                Takeoff(self.autopilot, 200), 
                lambda : self.relative_alt > 100
            ),
            WaypointStage(
                FlyTo(self.autopilot, waypoint, 200), 
                lambda : self.distance_to(waypoint) < 5
            ),
            WaypointStage(
                SetMode(self.autopilot, Modes.LAND),
                lambda : self.flightstage == \
                    mavutil.mavlink.MAV_LANDED_STATE_ON_GROUND
            )
        ]

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

    def update_waypoint_loop(self):
        """Performs updates on our mission status and issues commands as 
        necessary"""
        while True:
            if not self.current_stage or self.current_stage.done():
                self.get_new_instruction()
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
        if self.debug:
            self.waypoints.put(Waypoint(51.0455656,-114.07079236))
            self.waypoints.put(Waypoint(51.1455656,-114.17079236))

        print("Running")
        self.heartbeat_thread.start()
        self.send_command_thread.start()
        self.read_command_thread.start()
        self.update_waypoint_thread.start()

        while True:
            pass
