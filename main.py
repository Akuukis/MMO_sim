#!/usr/bin/python3

import math
import random
import json
import threading
import importlib
import time
from datetime import datetime
import traceback
from queue import Queue
from jsmin import jsmin
from pprintpp import pprint as pp

import cp

tick = 0

# lock to serialize console output
lock = threading.Lock()

# Threading
def worker():
    while True:
        libraryOrFn = q.get()
        start = time.time()
        if libraryOrFn == False:
            q.task_done()
            break  # Die
        elif type(libraryOrFn) is str:
            try:
                part = importlib.__import__(libraryOrFn)
                log = part.main(tick, config, q)
                with lock:
                    print("> %7.5f for %s: %s" % (time.time() - start, libraryOrFn, log))
            except Exception as e:
                with lock:
                    print("Error for "+str(libraryOrFn)+": "+str(e))
                    traceback.print_exc()
            finally:
                q.task_done()
        else:
            try:
                log = libraryOrFn(tick, config, q)
                with lock:
                    print("~ %7.5f for %s (%s)" % (time.time() - start, log, str(libraryOrFn)))
            except Exception as e:
                with lock:
                    print("Error for "+str(libraryOrFn)+": "+str(e))
                    traceback.print_exc()
            finally:
                q.task_done()

q = Queue()
while True:
    # Reload stuff ############################################################

    start = time.time()

    with open('config.json') as data_file:
        config = json.loads(jsmin(data_file.read()))

    # Respawn workers
    for i in range(config['num_worker_threads']):
         t = threading.Thread(target=worker)
         t.start()

    # Get tick
    try:
        tick = cp.query(payload="SELECT COUNT() FROM massive WHERE object == 'tick' GROUP BY object LIMIT 0, 1")["results"][0]["COUNT()"]
    except KeyError or TypeError:
        tick = 0

    # Update universe, create or age systems, stars, planets
    q.put('universe')

    # Check planets to spawn new Faction with Colony
    q.put('factions')

    # Production and upkeep
    q.put('economy')

    # Construction
    q.put('construction')

    # Ship movement
    q.put('ships')

    # Wait for all threads and kill all workers
    q.join()
    for i in range(config['num_worker_threads']):
        q.put(False)

    # Update tick
    cp.put(payload={'object': 'tick', 'value': time.time(), 'last': start})

    print("# %5d: %7.5f total." % (tick, time.time() - start))
    time.sleep(config['pauseTicks'])
    # tick ends ###################################################################
