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

def rndMaterials(solidsOther, MetalsIsotopes):
    weights = [] # Material weights, [0]: Solids, [1]: Metals, [2]: Isotopes
    weights.append(round(utils.dist_skewedLeft(solidsOther), 2))
    weights.append(round(utils.dist_skewedLeft(MetalsIsotopes) * (1-weights[0]), 2))
    weights.append(1 - weights[0] - weights[1])
    return weights

def main(tick, config, q):
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
                        "object": "moon",
                        "system_coords": rndCoords(config['moonDistance'], config['zFlatness']),
                        'type': ['Gas', 'Ice', 'Rock', 'Iron', 'Mix'][utils.choose_weighted(config['moonType'])],
                        'size': round(utils.dist_skewedLeft(config['moonSize']), 0),
                        'habitability': round(utils.dist_skewedLeft(config['moonHabitability']), 0),
                        'richness': round(utils.dist_skewedLeft(config['moonRichness']), 0),
                        'materials': rndMaterials(config['moonWeightSolidsOther'], config['moonWeightMetalsIsotopes']),
                    })
                planets.append({
                    "id": planet,
                    "object": "planet",
                    "system_coords": rndCoords(config['planetDistance'], config['zFlatness']),
                    "childs": moons,
                    'type': ['Gas', 'Ice', 'Rock', 'Iron', 'Mix'][utils.choose_weighted(config['planetType'])],
                    'size': round(utils.dist_skewedLeft(config['planetSize']), 0),
                    'habitability': round(utils.dist_skewedLeft(config['planetHabitability']), 0),
                    'richness': round(utils.dist_skewedLeft(config['planetRichness']), 0),
                    'materials': rndMaterials(config['planetWeightSolidsOther'], config['planetWeightMetalsIsotopes']),
                })
            stars.append({
                "id": star,
                "object": "star",
                "system_coords": rndCoords(config['starDistance'], config['zFlatness']),
                "childs": planets
            })
        universe['systems'].append({
            "id": system,
            "object": "system",
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

    # Workaround for scoping problems
    def workaround(payload, params, msg):
        q.put(lambda a, b, c: cp.put(payload=payload, params=params, msg=msg))

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
                    workaround(payload=moon, params=pre+urlm+"]", msg='      Moon ' + urlm)
                del planet["childs"]
                workaround(payload=planet, params=pre+urlp+"]", msg='    Planet ' + urlp)
            del star["childs"]
            workaround(payload=star, params=pre+urls+"]", msg='  Star ' + urls)
        del system["childs"]
        workaround(payload=system, params=pre+urly+"]", msg='System ' + urly)

if __name__ == "__main__":
    main()
