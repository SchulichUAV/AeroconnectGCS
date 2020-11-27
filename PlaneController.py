class PlaneController():
    def __init__(self, autopilot, server_address):
        self.autopilot = autopilot
        self.server_address = server_address
        # Queues are used to pass information in a threadsafe way from produces to consumers
        self.job_queue = PriorityQueue() # Priority queues are threadsafe so we don't need the workaround
        self.command_exit_queue = PriorityQueue() # List of commands and exit conditions. Exit conditions can be lambda function
        self.received_message_queue = Queue() # Messages received from the plane
        self.send_message_queue = Queue()
        self.server_jobs_queueu = Queue() # List of jobs received from server

        self.current_command = None
        self.next_command_condition = None # Are we ready for the next command?
        self.current_job = None
        self.next_job_condition = None # Are we ready for the next job?
    
    def run(self):
        # Threads we need to run are
        # heartbeat
        # get_new_jobs (polls the server)
        # get_plane_stats (poll planes for params or whatever)
        # post_plane_stats (send plane stats to the server)
        # check_command_done : check if the exit condition is met and if so get current_cmd from the command queue
        # check_job_done : check if the current job is done and if so grab the next one - needs to convert it to commands
        # parse_commands : parsed the received commands queue for stats about the plane
        # handle_plane_commands : parse messages received from plane
        pass
