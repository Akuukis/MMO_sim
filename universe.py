#!/usr/bin/python3

import math
import random
from pprintpp import pprint as pp

import cp
import utils

def rndCoords(distance, zFlatness):
    distance = random.randrange(distance[0],distance[1])
    x = utils.rnd()
    y = utils.rnd()
    z = utils.rnd() * zFlatness
    l = math.fabs(x**3 + y**3 + z**3)**(1/3)
    k = distance / l
    return {"x":float(x*k), "y":float(y*k), "z":float(z*k)}

def main(tick, config):
    universe = {
        "tick": 0,
        "systems": []
    }
    # Generate universe
    for system in range(0, int(utils.dist_skewedLeft(config['systems']))):
        stars = []
        for star in range(0, int(utils.dist_skewedLeft(config['stars']))):
            planets = []
            for planet in range(0, int(utils.dist_skewedLeft(config['planets']))):
                moons = []
                for moon in range(0, int(utils.dist_skewedLeft(config['moons']))):
                    moons.append({
                        "id": moon,
                        "type": "moon",
                        "system_coords": rndCoords(config['moonDistance'], config['zFlatness'])
                    })
                planets.append({
                    "id": planet,
                    "type": "planet",
                    "system_coords": rndCoords(config['planetDistance'], config['zFlatness']),
                    "childs": moons,
                })
            stars.append({
                "id": star,
                "type": "star",
                "system_coords": rndCoords(config['starDistance'], config['zFlatness']),
                "childs": planets
            })
        universe['systems'].append({
            "id": system,
            "type": "system",
            "universe_coords": {
                "x": random.randrange(config['x'][0],config['x'][1]),
                "y": random.randrange(config['y'][0],config['y'][1]),
                "z": random.randrange(config['z'][0],config['z'][1]),
            },
            "childs": stars
        })


    #pp = pprint.PrettyPrinter(indent=4)
    #print(pp.pprint(universe))
    #print("\n")
    #conn.set_debuglevel(10)

    # Insert universe in database
    pre = '[t' + str(universe['tick'])
    for system in universe["systems"]:
        urly = 'y' + str(system["id"])
        for star in system["childs"]:
            urls = urly + 's' + str(star["id"])
            for planet in star["childs"]:
                urlp = urls + 'p' + str(planet["id"])
                for moon in planet["childs"]:
                    urlm = urlp + 'm' + str(moon["id"])
                    cp.put(payload=moon, params=pre+urlm+"]", msg='      Moon ' + urlm)
                del planet["childs"]
                cp.put(payload=planet, params=pre+urlp+"]", msg='    Planet ' + urlp)
            del star["childs"]
            cp.put(payload=star, params=pre+urls+"]", msg='  Star ' + urls)
        del system["childs"]
        cp.put(payload=system, params=pre+urly+"]", msg='System ' + urly)

if __name__ == "__main__":
    main()
