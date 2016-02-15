#!/usr/bin/python

import math
import Entity

class Ship(Entity):
    def __init__(self):
        self.location_starsystem = None # where are we in grand scheme of things
        self.travel_between_starsystems = False # are we traveling between starsystems
        self.from_starsystem = None # traveling from starsystem
        self.to_starsystem = None # traveling to starsystem
        self.distance_to_starsystem = 0 # if traveling between starsystems, how far you are
        self.speed = 0 # how much ship travels per tick
        self.target_coordinates = {"x": 0, "y": 0,"z": 0} # Target coordinates where you travel to
    
    def travel(self):
        distance_between = sqrt((self.system_coordinates["x"] -self.target_coordinates["x"])^2 + (self.system_coordinates["y"] -self.target_coordinates["y"])^2 + (self.system_coordinates["z"] -self.target_coordinates["z"])^2)
        part_of_distance = self.speed/distance_between
        new_coordinates = { "x": self.target_coordinates["x"] + ((self.target_coordinates["x"] - self.system_coordinates["x"]) * part_of_distance), "y": self.target_coordinates["y"] + ((self.target_coordinates["y"] - self.system_coordinates["y"]) * part_of_distance), "z": self.target_coordinates["z"] + ((self.target_coordinates["z"] - self.system_coordinates["z"]) * part_of_distance)}
        self.system_coordinates = new_coordinates

    def travel_interstellar(self):

    def life_cycle(self):
        self.travel(self)

class Fighter(Ship):
    def __init__(self):
        self.has_weapons = True
    
    def combat(self):
    
    def life_cycle(self):
        super(Ship,self).life_cycle()

class PatrolShip(Fighter):
	def __init__(self):
		self.target_systemcenter = True # by default we just loop between station and center
		self.target_threat = False # if threat is detected, we fly towards it...it's totally safe
        self.base = None # Colony based object 

	def detect_threat(self):
		list_of_ships = get_ships_nearby(self.location_starsystem, self.distance)
		# TODO which one is threat

	def life_cycle(self):
		super(Fighter,self).life_cycle()
        # after travel we have reached center we return to station
        if(self.system_coordinates["x"] == 0 and self.system_coordinates["y"] == 0 and self.system_coordinates["z"] == 0):
            self.system_coordinates = {"x": self.base.system_coordinates["x"], "y": self.base.system_coordinates["y"], "z": self.base.system_coordinates["z"]}
		self.detect_threat(self)
		self.combat(self)
