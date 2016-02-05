#!/usr/bin/python3

import random
from pprintpp import pprint as pp

import cp
import utils

def rndCoords(distance, zFlatness):
    distance = random.randrange(distance[0],distance[1])
    x = utils.rnd()
    y = utils.rnd()
    z = utils.rnd() * zFlatness
    l = (x**3 + y**3 + z**3)**(1/3)
    k = distance / l
    return [x*k, y*k, z*k]

def main(tick, config):
    universe = {
        "lastSystemId": 0,
        "systems": []
    }
    # Generate universe
    for system in range(1, int(utils.dist_skewedLeft(config['systems']))):
        stars = []
        for star in range(1, int(utils.dist_skewedLeft(config['stars']))):
            planets = []
            for planet in range(1, int(utils.dist_skewedLeft(config['planets']))):
                moons = []
                for moon in range(1, int(utils.dist_skewedLeft(config['moons']))):
                    coords = rndCoords(config['moonDistance'], config['zFlatness'])
                    moons.append({
                        "id": moon,
                        "type": "moon",
                        "x": coords['x'],
                        "y": coords['y'],
                        "z": coords['z'],
                    })
                coords = rndCoords(config['planetDistance'], config['zFlatness'])
                planets.append({
                    "id": planet,
                    "type": "planet",
                        "x": coords['x'],
                        "y": coords['y'],
                        "z": coords['z'],
                    "childs": moons,
                })
            coords = rndCoords(config['starDistance'], config['zFlatness'])
            stars.append({
                "id": star,
                "type": "star",
                        "x": coords['x'],
                        "y": coords['y'],
                        "z": coords['z'],
                "childs": planets
            })
        universe['lastSystemId'] += 1
        universe['systems'].append({
            "id": system,
            "type": "system",
            "x": random.randrange(config['x'][0],config['x'][1]),
            "y": random.randrange(config['y'][0],config['y'][1]),
            "z": random.randrange(config['z'][0],config['z'][1]),
            "childs": stars
        })


    #pp = pprint.PrettyPrinter(indent=4)
    #print(pp.pprint(universe))
    #print("\n")
    #conn.set_debuglevel(10)

    # Insert universe in database
    for system in universe["systems"]:
        for star in system["childs"]:
            for planet in star["childs"]:
                for moon in planet["childs"]:
                    urlid = "[" + 'y' + str(system["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + 'm' + str(moon["id"]) + "]"
                    cp.put(payload=moon, params=urlid, msg='      Moon ' + urlid)
                del planet["childs"]
                urlid = "[" + 'y' + str(system["id"]) + 's' + str(star["id"]) + 'p' + str(planet["id"]) + "]"
                cp.put(payload=planet, params=urlid, msg='    Planet ' + urlid)
            del star["childs"]
            urlid = "[" + 'y' + str(planet["id"]) + 's' + str(star["id"]) + "]"
            cp.put(payload=star, params=urlid, msg='  Star ' + urlid)
        del system["childs"]
        urlid = "[" + 'y' + str(system["id"]) + "]"
        cp.put(payload=system, params=urlid, msg='System ' + urlid)

if __name__ == "__main__":
    main()
