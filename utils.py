import random
import time
import traceback
import importlib
import threading
from queue import Queue

def rnd():
    return random.random()*2-1

def dist_flat(array):
    return array[0]+rnd()*array[1]

def dist_skewedLeft(array):
    return 0 + array[0]*array[1]**rnd()

def dist_skewedRight(array):
    return array[0]*array[1] - array[0]*array[1]**rnd()

def choose_weighted(array):
    # Assume number in array sum to 1
    pick = random.random()
    cum = 0
    for i,v in enumerate(array):
        cum += v
        if pick < cum:
            return i

def rto11(minus, plus):  # (0, inf) to [-1; 1]
    if minus > plus:
        return -1 + plus/minus
    else
        return  1 - minus/plus

# Threading
lock = threading.Lock()
q = Queue()
def worker(*args):
    while True:
        libraryOrFn = q.get()
        start = time.time()
        if libraryOrFn == False:
            q.task_done()
            break  # Die
        elif type(libraryOrFn) is str:
            try:
                part = importlib.__import__(libraryOrFn)
                log = part.main(*args)
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
                log = libraryOrFn()
                with lock:
                    print("~ %7.5f for %s" % (time.time() - start, log))
            except Exception as e:
                with lock:
                    print("Error for "+str(libraryOrFn)+": "+str(e))
                    traceback.print_exc()
            finally:
                q.task_done()

def spawn_workers(n, *args):
    # Respawn workers
    for i in range(n):
        t = threading.Thread(target=worker, args=tuple(args))
        t.start()

def kill_workers(n):
    for i in range(n):
        q.put(False)

def queue(fn, *args, **kwargs):
    q.put(lambda: fn(*args, **kwargs))

def main(tick):
    pass

if __name__ == "__main__":
    main()