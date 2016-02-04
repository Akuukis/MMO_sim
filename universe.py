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
    # prepare copy of dict, as we want to remove childs
    preparestarsystem = copy.deepcopy(starsystem)
    del preparestarsystem["childs"]
    urlid = "[" + 'y' + str(starsystem["id"]) + "]"
    r = requests.post(url + urlid, json=preparestarsystem, auth=(username, password))
    if r.json()['error']:
        pp(r.json())
    else:
        print('System ' + urlid)

    for star in starsystem["childs"]:
        # insert star
        # prepare copy of dict, as we want to remove childs
        preparestar = copy.deepcopy(star)
        del preparestar["childs"]
        urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + "]"
        r = requests.post(url + urlid, json=preparestar, auth=(username, password))
        if r.json()['error']:
            pp(r.json())
        else:
            print('  Star ' + urlid)

        for planet in star["childs"]:
            # insert planet
            # prepare copy of dict, as we want to remove childs
            prepareplanet = copy.deepcopy(planet)
            del prepareplanet["childs"]
            urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + "]"
            r = requests.post(url + urlid, json=preparestar, auth=(username, password))
            if r.json()['error']:
                pp(r.json())
            else:
                print('    Planet ' + urlid)
            for moon in planet["childs"]:
                # insert moon
                # convert to json
                raw_data = json.dumps(moon)
                urlid = "[" + 'y' + str(starsystem["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + 'm' + str(moon["id"]) + "]"
                r = requests.post(url + urlid, json=preparestar, auth=(username, password))
                if r.json()['error']:
                    pp(r.json())
                else:
                    print('      Moon ' + urlid)