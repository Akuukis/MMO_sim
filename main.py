#!/usr/bin/python3

import math
import random
import json
import threading
import importlib
import time
from queue import Queue
from jsmin import jsmin
from pprintpp import pprint as pp

# Resources ###################################################################

item = {
    'type': 'ship' or 'part',
    'subtype': 123456789,  # id of model.
    'amount': 1
}

# Entities ####################################################################

pc = {
    'id': 1,
    'coords': [0, 0, 0]
}

ship = {
    'coords': [0, 0, 0],
    'type': 'freight' or 'settler' or 'corvette' or 'frigate',  # Corvette small tank, Frigate big tank, guns similar
    'storage': {
        'goods': {
        },
        'solids': 0,  # Upkeep for industry
        'metals': 0,  # For structure of skips
        'isotopes': 0,  # For guns of ships
        'ammo': 1000  # For guns to shoot
    }
}

colony = {
    'anchor': False,  # Planet, moon or orbit colony is attached to.
    'id': 10000123,
    'population': 1,
    'industry': 1,
    'ships': [ship, ship],
    'storage': {
        'goods': {
            10000123: 100,
            10000777: 100,
            10000888: 100,
            10000999: 100,
        },
        'solids': 50,  # Upkeep for industry
        'metals': 30,  # For structure of skips
        'isotopes': 20,  # For guns of ships
        'ammo': 0  # For guns to shoot
    }
}

faction = {
    'colonies': [colony, colony],
    'pref': {  # 0 prefers first, 1 prefers last, 0.5 is indifferent.
        'population_industry': 0.5,  # At what ratio (weighted by habitability and richness) to keep industry
        'pacific_militaristic': 0.5,  # Size of warfleet to keep
        'defence_attack': 0.5,  # Ratio of created warships to dedicate for defence
        'growth_expand': 0.5,  # At what % of optimalPopulation to grow further or create settler
    }
}

# Statics #####################################################################

moon = {
    'coords': [0, 0, 0],  # in LS relative to system
    'type': 'Gas' or 'Ice' or 'Rock' or 'Iron' or 'Mix',  # Colonize only home planet type. Gas by none, Mix by all
    'size': 3,  # Also maxSize for colony
    'habitability': 0.9,  # Modifier to good generation for colony
    'richness': 1.5,  # Modifier to raw material generation for colony
    'weightSolids': 0.5,  # Modifier to solid generation for colony. Solid+Metal+Radioactive = 1
    'weightMetals': 0.3,  # Modifier to metal generation for colony. Solid+Metal+Radioactive = 1
    'weightIsotopes': 0.2,  # Modifier to radioactive generation for colony. Solid+Metal+Radioactive = 1
    'colony': False
}

planet = {
    'moons': [moon, moon],
    'coords': [0, 0, 0],  # in LS relative to system
    'type': 'Gas' or 'Ice' or 'Rock' or 'Iron' or 'Mix',  # Colonize only home planet type. Gas by none, Mix by all
    'size': 10,  # = maxSize = (population + industry) for colony
    'habitability': 0.9,  # Modifier to good generation for colony
    'richness': 1.5,  # Modifier to raw material generation for colony
    'weightSolids': 0.5,  # Modifier to solid generation for colony. Solid+Metal+Radioactive = 1
    'weightMetals': 0.3,  # Modifier to metal generation for colony. Solid+Metal+Radioactive = 1
    'weightIsotopes': 0.2,  # Modifier to radioactive generation for colony. Solid+Metal+Radioactive = 1
    'colony': False,
}

star = {
    'planets': [planet, planet],
    'coords': [0, 0, 0],  # in LS relative to system
}

system = {
    'stars': [star, star],
    'coords': [0, 0, 0],  # in LY relative to universe
}

universe = {
    'systems': [system, system],
    'factions': [faction, faction]
}

# function ####################################################################


def choose_weighted(array):
    # Should be array of [weight, answer]
    total = 0
    for item in array:
        total += item[0]
    chosen = random.randint(0, total)
    for item in array:
        total -= item[0]
        if total < chosen:
            return item[1]

# routines ####################################################################


def ms():
    from datetime import datetime
    dt = datetime.utcnow()
    return dt.hour * 60 * 60 + dt.minute * 60 + dt.second + dt.microsecond / 1000000


def upkeep_population(colony):
    size = colony.population
    for key, amount in colony.storage.goods:
        if colony.storage.goods[key] >= 1 and random.random() >= 0.5:
            colony.storage.goods[key] -= 1
            size -= 1
            if size == 0:
                return
    if colony.storage.goods[colony.id].amount >= 4 * size:
        colony.storage.goods[colony.id].amount -= 4 * size
    else:
        degrade_population(colony)


def upkeep_industry(colony):
    size = colony.industry
    for key, amount in colony.storage.goods:
        if colony.storage.goods[key] >= 1 and random.random() >= 0.5:
            colony.storage.goods[key] -= 1
            size -= 1
            if size == 0:
                return
    if colony.storage.solids >= 4 * size:
        colony.storage.solids -= 4 * size
    else:
        degrade_industry(colony)


def produce_goods(colony):
    produce = 10 * colony.population * (colony.anchor.habitability - colony.population / 10)
    colony.storage.goods[colony.id].amount += produce


def produce_materials(colony):
    colony.storage.solids += 10 * colony.industry * colony.anchor.richness * colony.anchor.weightSolids
    colony.storage.metals += 10 * colony.industry * colony.anchor.richness * colony.anchor.weightMetals
    colony.storage.isotopes += 10 * colony.industry * colony.anchor.richness * colony.anchor.weightIsotopes


def upgrade_colony(colony, faction):
    if colony.anchor.size < colony.population + colony.industry:
        if colony.storage.solids >= 1000 and colony.storage.goods[colony.id].amount >= 1000:
            notfull = colony.population < colony.anchor.habitability / 2
            wantPopulation = faction.pref.population_industry * colony.anchor.habitability / colony.anchor.richness
            if notfull and colony.population < wantPopulation:
                upgrade_population(colony)
            else:
                upgrade_industry(colony)
            colony.storage.goods[colony.id].amount -= 1000
            colony.storage.solids -= 1000


def create_ships(colony, faction):
    # TODO AI
    pass


# undefined functions #########################################################


def upgrade_population(colony):
    pass


def upgrade_industry(colony):
    pass


def destroy_colony(colony):
    pass


def degrade_industry(colony):
    if colony.industry <= 1:
        destroy_colony(colony)
    pass


def degrade_population(colony):
    if colony.population <= 1:
        destroy_colony(colony)
    pass


def get_all_planets():
    pass


def get_all_colonies():
    pass


def get_all_factions():
    pass


def get_vector(object, target):
    pass


def spawn_faction():
    pass


def spawn_colony():
    pass


# lock to serialize console output
lock = threading.Lock()
q = Queue()
tick = 0
while True:
    # Reload stuff ############################################################

    start = ms()

    with open('config.json') as data_file:
        config = json.loads(jsmin(data_file.read()))

    def worker(library):
        q.get()
        start = ms()
        part = importlib.__import__(library)
        log = part.main(tick, config)
        with lock:
            print("       %7.5f for %s." % (ms() - start, library))
        q.task_done()

    def spawn_worker(library):
        q.put(True)
        t = threading.Thread(target=worker, args=(library,))
        # t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
        t.start()


    # Update universe, create or age systems, stars, planets
    spawn_worker('universe')

    # Check planets to spawn new Faction with Colony
    spawn_worker('spawn_factions')

    # Production and upkeep
    spawn_worker('economy')

    # Construction
    spawn_worker('construction')

    # Ship movement
    spawn_worker('ships')

    # Wait for all threads
    q.join()

    # Update tick
    tick = tick + 1
    print("%5d: %7.5f total." % (tick, ms() - start))
    time.sleep(0.01)
    # tick ends ###################################################################
