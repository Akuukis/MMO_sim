#!/usr/bin/python

import random
import pprint
import httplib, urllib
import base64
import string
import json
import sys
import copy

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
host = "xxx.xxx.xxx.xxx"
username = "root"
password = "password"
port = "5580"
auth = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
url = "/v4/1/massive"

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
    conn = httplib.HTTPConnection(host, port)
    # insert starsystem
    # prepare copy of dict, as we want to remove childs
    preparestarsystem = copy.deepcopy(starsystem)
    del preparestarsystem["childs"]
    # convert to json
    raw_data = json.dumps(preparestarsystem)
    urlwithid = url + "[" + str(starsystem["id"]) + "]"
    conn.putrequest('POST', urlwithid)
    headers = {"Authorization": "Basic %s" % auth, "Content-Length": str(len(raw_data))}
    for k in headers:
            conn.putheader(k, headers[k])
    conn.endheaders()    
    conn.send(raw_data)
    conn.close()
    for star in starsystem["childs"]:
        conn = httplib.HTTPConnection(host, port)
        # insert star
        # prepare copy of dict, as we want to remove childs
        preparestar = copy.deepcopy(star)
        del preparestar["childs"]
        # convert to json
        raw_data = json.dumps(preparestar)
        urlwithid = url + "[" + str(starsystem["id"]) + str(star["id"]) + "]"
        conn.putrequest('POST', urlwithid)
        headers = {"Authorization": "Basic %s" % auth, "Content-Length": str(len(raw_data))}
        for k in headers:
            conn.putheader(k, headers[k])
        conn.endheaders()    
        conn.send(raw_data)
        conn.close()
        for planet in star["childs"]:
            conn = httplib.HTTPConnection(host, port)
            # insert planet
            # prepare copy of dict, as we want to remove childs
            prepareplanet = copy.deepcopy(planet)
            del prepareplanet["childs"]
            # convert to json
            raw_data = json.dumps(prepareplanet)
            urlwithid = url + "[" + str(starsystem["id"]) + str(star["id"]) + str(planet["id"]) + "]"
            conn.putrequest('POST', urlwithid)
            headers = {"Authorization": "Basic %s" % auth, "Content-Length": str(len(raw_data))}
            for k in headers:
                conn.putheader(k, headers[k])
            conn.endheaders()    
            conn.send(raw_data)
            conn.close()
            for moon in planet["childs"]:
                conn = httplib.HTTPConnection(host, port)
                # insert moon
                # convert to json
                raw_data = json.dumps(moon)
                urlwithid = url + "[" + str(starsystem["id"]) + str(star["id"]) + str(planet["id"]) + str(moon["id"]) + "]"
                conn.putrequest('POST', urlwithid)
                headers = {"Authorization": "Basic %s" % auth, "Content-Length": str(len(raw_data))}
                for k in headers:
                    conn.putheader(k, headers[k])
                conn.endheaders()    
                conn.send(raw_data)
                conn.close()
conn.close()
