#!/usr/bin/python

class Entity:
    def __init__(self):
        self.system_coordinates = {"x": 0, "y": 0,"z": 0} # where we are in system
        self.galactic_coordinates = {"x": 0, "y": 0,"z": 0} #where we are in galaxy
