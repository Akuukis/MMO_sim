#!/usr/bin/python3

import math
import random
from pprintpp import pprint as pp

import cp
import utils

def rndCoords(distance, zFlatness, center={"x":0,"y":0,"z":0}):
    distance = random.randrange(distance[0],distance[1])
    x = utils.rnd()
    y = utils.rnd()
    z = utils.rnd() * zFlatness
    l = math.fabs(x**3 + y**3 + z**3)**(1/3)
    k = distance / l
    return {
        "radius":distance,
        "x":float(x*k+center["x"]),
        "y":float(y*k+center["y"]),
        "z":float(z*k+center["z"])
    }

def rndMaterials(solidsOther, MetalsIsotopes):
    weights = [] # Material weights, [0]: Solids, [1]: Metals, [2]: Isotopes
    weights.append(round(utils.dist_skewedLeft(solidsOther), 2))
    weights.append(round(utils.dist_skewedLeft(MetalsIsotopes) * (1-weights[0]), 2))
    weights.append(round(1 - weights[0] - weights[1], 2))
    return weights

def main(tick, config, q):
    # How many systems are there?
    count = int(cp.query(payload="SELECT * FROM massive WHERE object == 'system' LIMIT 0, 0")["hits"])

    # How many we want?
    want = int(utils.dist_skewedLeft(config['systems']))

    if want == count:
        pass
    elif want >= count:
        # Generate up to X more systems per tick
        pre = '[t' + str(tick)
        for system in range(0, max(1, round((want - count)/config['beatUniverse']))):
            urly = 'y' + str(system)
            stars = []
            for star in range(0, int(utils.dist_skewedLeft(config['stars']))):
                urls = urly + 's' + str(star)
                coordss = rndCoords(config['starDistance'], config['zFlatness'])
                planets = []
                for planet in range(0, int(utils.dist_skewedLeft(config['planets']))):
                    urlp = urls + 'p' + str(planet)
                    coordsp = rndCoords(config['planetDistance'], config['zFlatness'], coordss)
                    moons = []
                    for moon in range(0, int(utils.dist_skewedLeft(config['moons']))):
                        urlm = urlp + 'm' + str(moon)
                        utils.queue(cp.put, payload={
                                "object": "moon",
                                "system_coords": rndCoords(config['moonDistance'], config['zFlatness'], coordsp),
                                'type': ['Gas', 'Ice', 'Rock', 'Iron', 'Mix'][utils.choose_weighted(config['moonType'])],
                                'size': round(utils.dist_skewedLeft(config['moonSize']), 0),
                                'habitability': round(utils.dist_skewedLeft(config['moonHabitability']), 1),
                                'richness': round(utils.dist_skewedLeft(config['moonRichness']), 1),
                                'materials': rndMaterials(config['moonWeightSolidsOther'], config['moonWeightMetalsIsotopes']),
                            },
                            params=pre+urlm+"]",
                            msg='      Moon ' + pre+urlm+"]"
                        )
                    utils.queue(cp.put, payload={
                            "object": "planet",
                            "system_coords": rndCoords(config['planetDistance'], config['zFlatness']),
                            'type': ['Gas', 'Ice', 'Rock', 'Iron', 'Mix'][utils.choose_weighted(config['planetType'])],
                            'size': round(utils.dist_skewedLeft(config['planetSize']), 0),
                            'habitability': round(utils.dist_skewedLeft(config['planetHabitability']), 1),
                            'richness': round(utils.dist_skewedLeft(config['planetRichness']), 1),
                            'materials': rndMaterials(config['planetWeightSolidsOther'], config['planetWeightMetalsIsotopes']),
                        },
                        params=pre+urlp+"]",
                        msg='    Planet ' + pre+urlp+"]"
                    )
                utils.queue(cp.put, payload={
                        "id": star,
                        "object": "star",
                        "system_coords": rndCoords(config['starDistance'], config['zFlatness']),
                    },
                    params=pre+urls+"]",
                    msg='  Star ' + pre+urls+"]"
                )
            utils.queue(cp.put, payload={
                "object": "system",
                "universe_coords": {
                    "x": random.randrange(config['x'][0],config['x'][1]),
                    "y": random.randrange(config['y'][0],config['y'][1]),
                    "z": random.randrange(config['z'][0],config['z'][1]),
                },},
                params=pre+urly+"]",
                msg='System ' + pre+urly+"]"
            )
    elif want <= count:
        pass  # TODO destroy systems

    return "done"

if __name__ == "__main__":
    main()
