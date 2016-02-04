#!/usr/bin/python

import random
import requests
import base64
import json
import copy
from pprintpp import pprint as pp

def generateSystemName():
    names = ["Stellar", "Forge", "Sol", "Indeae", "Caseopae", "Alpha", "Centauris", "HTC", "Eagle"]
    return random.choice(names) + " " + random.choice(names)

def generateStarName():
    names = ["Stellar", "Forge", "Sol", "Indeae", "Caseopae", "Alpha", "Centauris", "HTC", "Eagle"]
    return random.choice(names) + " " + random.choice(names)

def generatePlanetName():
    names = ["Stellar", "Forge", "Sol", "Indeae", "Caseopae", "Alpha", "Centauris", "HTC", "Eagle"]
    return random.choice(names) + " " + random.choice(names)

def generateMoonName():
    names = ["Stellar", "Forge", "Sol", "Indeae", "Caseopae", "Alpha", "Centauris", "HTC", "Eagle"]
    return random.choice(names) + " " + random.choice(names)

def post(url, payload, msg=None, errorMsg=None):
    r = requests.post(url, json=payload, auth=(username, password))
    if not r.json()['error']:
        if msg:
            print(msg)
    else:
        pp(r.json())
        if errorMsg:
            print(errorMsg)

universe = {}
universe["starsystems"]= []
number_of_max_stars = 10
number_of_max_planets = 10
number_of_max_moons = 10

# Clusterpoint connection data
host = "192.168.7.58"
username = "root"
password = "password"
port = "5580"
path = "v4/1/massive"
url = "http://" + host + ":" + port + "/" + path

for starsystemid in range (1, 1000):
    # generate galactic coordinates
    x = random.randrange(4,110000)
    y = random.randrange(4,110000)
    z = random.randrange(0,100)
    # getting name for star system
    newstarsystem = {"objectName": generateSystemName(), "id": starsystemid, "type": "starsystem", "x": x, "y": y, "z": z}
    # getting stars in system
    random_stars = random.randrange(1, number_of_max_stars)
    stars = []
    for starsnr in range (1, random_stars):
        distance = random.randrange(110, 1200000)
        newstar = {"objectName": generateStarName(), "id": starsnr, "type": "star", "distance": distance}
        stars.append(newstar)
        random_planets = random.randrange(1, number_of_max_planets)
        planets = []
        # getting planets for each star
        for planetsnr in range (1, random_planets):
            distance = random.randrange(110, 40320)
            newplanet = {"objectName": generateStarName(), "id": planetsnr, "type": "planet", "distance": distance}
            planets.append(newplanet)
            moons = []
            random_moons = random.randrange(1, number_of_max_moons)
            for moonsnr in range (1, random_moons):
                distance = random.randrange(200000, 500000)
                newmoon = {"objectName": generateMoonName(), "id": moonsnr, "type": "moon", "distance": distance}
                moons.append(newmoon)
            newplanet["childs"] = moons
        newstar["childs"] = planets
    newstarsystem["childs"] = stars

    universe["starsystems"].append(newstarsystem)

#pp = pprint.PrettyPrinter(indent=4)
#print(pp.pprint(universe))
#print("\n")
#conn.set_debuglevel(10)

# Insert data in database
for starsystem in universe["starsystems"]:
    preparestarsystem = copy.deepcopy(starsystem)  # prepare copy of dict, as we want to remove childs
    del preparestarsystem["childs"]
    urlid = "[" + 'y' + str(starsystem["id"]) + "]"
    post(url + urlid, preparestarsystem, 'System ' + urlid)

    for star in starsystem["childs"]:
        preparestar = copy.deepcopy(star)
        del preparestar["childs"]
        urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + "]"
        post(url + urlid, preparestar, '  Star ' + urlid)

        for planet in star["childs"]:
            prepareplanet = copy.deepcopy(planet)
            del prepareplanet["childs"]
            urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + "]"
            post(url + urlid, prepareplanet, '    Planet ' + urlid)

            for moon in planet["childs"]:
                urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + 'm' + str(moon["id"]) + "]"
                post(url + urlid, moon, '      Moon ' + urlid)