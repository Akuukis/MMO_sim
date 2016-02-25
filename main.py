#!/usr/bin/python3

import json
import time
from jsmin import jsmin
from pprintpp import pprint as pp

import cp
import utils

tick = 0

# lock to serialize console output
while True:
    # Reload stuff ############################################################

    start = time.time()

    with open('config.json') as data_file:
        config = json.loads(jsmin(data_file.read()))

    # Get tick
    try:
        tick = cp.query(payload="SELECT COUNT() FROM massive WHERE object == 'tick' GROUP BY object LIMIT 0, 1")["results"][0]["COUNT()"]
    except KeyError or TypeError:
        tick = 0

    # Respawn workers
    utils.spawn_workers(config['num_worker_threads'], tick, config, utils.q)

    # Update universe, create or age systems, stars, planets
    # Per beat, create/destroy systems to match wanted amount
    utils.q.put('universe')

    # Check planets to spawn new Faction with Colony
    # Per beat, spawn factions to match wanted amount (if planets allows)
    # Per beat, check every faction for disbanding
    utils.q.put('factions')

    # Production and upkeep
    # Per beat, colony 50% upkeep 2*batch or 50% produce 2*batch
    utils.q.put('economy')

    # Construction
    utils.q.put('construction')

    # Ship movement
    utils.q.put('ships')

    # Wait for all threads and kill all workers
    utils.q.join()
    utils.kill_workers(config['num_worker_threads'])

    # Update tick
    cp.put(payload={'object': 'tick', 'value': time.time(), 'last': start})

    print("# %5d: %7.5f total." % (tick, time.time() - start))
    time.sleep(config['pauseTicks'])
    # tick ends ###################################################################
