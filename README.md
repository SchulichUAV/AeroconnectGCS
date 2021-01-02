# Aeroconnect GCS
## About this Project
Aeroconnect GCS was designed as part of the [SAE AeroConnect 2021 Challenge](https://www.sae.org/attend/student-events/aeroconnect-challenge/). This software serves as an interface between a dedicated flight controller responsible for the low level details of flight (rotor speed, reading sensor values) and a server which tells the aircraft where to fly. Aeroconnect GCS is responsible for
- Polling the server for new waypoints to fly to
- Translating the waypoints into a list of commands to the flight controller
- Updating the server with the aircraft status

Note that GCS is a bit of a misnomer since this software is running on the plane, not on a ground control station.
## Getting started
To get an idea of how the software works you can use [SITL](https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html) to simulate an aircraft. Before following the steps below, make sure you understand and can use SITL.

In a terminal start SITL
```
cd ardupilot/ArduCopter
sim_vehicle.py -L Calgary --map --console
```
Once our plane has received a valid GPS reading we can start the GCS software in a separate terminal.
```
cd AeroconnectGCS
./main.py
``` 
If debug is set to true in main.py, we will see the plane takeoff, fly to the first location, land, takeoff again and then fly to the second location. This simulates flying to a location, picking up some passengers and then flying to another location. These locations have been hardcoded for testing.
## Contributing
### Contribution guidelines
Contributions are more than welcome. Currently we don't have a testing framework (although you could add one!). Please just test your additions with SITL. The only formal formatting rule is to have a maximum column width of 80 characters. I suggesting adding an 80 character editor ruler to your IDE. The code ownder is Zachary Lau (zlau2000@gmail.com).
### Tour of the code
The program is started by running main.py. This creates a PlaneController object which creates several threads. The PlaneController run method starts these threads. A quick descrption for each thread is shown below
#### heartbeat_thread
This thread sends a heartbeat to the aircraft every second. This is necessary for proper behaviour of the flight controller.
#### send_command_thread
This thread takes commands from the command_queue and sends them to the plane. This is the only thread that should be using the pymavlink send methods since they are not threadsafe as far as I can tell. If another thread wants to send a message it must be placed on the command_queue.
#### read_command_thread
This thread reads commands received from the plane and dispatches them to an appropriate handler function.
#### update_waypoint_thread
This thread handles our navigation. It keeps track of which stage of our mission the plane is on and when we need to move to the next stage.
