#!/usr/bin/python3

import random
from pprintpp import pprint as pp

import cp
import utils

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
                    moons.append({
                        "id": moon,
                        "type": "moon",
                        "distance": int(random.randrange(config['moonDistance'][0],config['moonDistance'][1]))
                    })
                planets.append({
                    "id": planet,
                    "type": "planet",
                    "distance": int(random.randrange(config['planetDistance'][0],config['planetDistance'][1])),
                    "childs": moons,
                })
            stars.append({
                "id": star,
                "type": "star",
                "distance": int(random.randrange(config['starDistance'][0],config['starDistance'][1])),
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
