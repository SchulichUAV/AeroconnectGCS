#!/usr/bin/env python3
# We do all our mavlink imports and dialect setting in this file so that we 
# ensure we are using the same dialects

from pymavlink import mavutil
mavutil.set_dialect("common")
# Define a global mav in this file to access the functions we need
mav = mavutil.mavlink.MAVLink