#! /usr/bin/env python3
# Utility classes for commonly used messages

from Jobs import MessageJob

class Heartbeat(MessageJob):
    def __init__(self, connection):
        super(connection, 6, 8, 102, 0, 4, 3)