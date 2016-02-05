import random

def rnd():
	return random.random()*2-1

def dist_flat(array):
	return array[0]+rnd()*array[1]

def dist_skewedLeft(array):
	return 0 + array[0]*array[1]**rnd()

def dist_skewedRight(array):
	return array[0]*array[1] - array[0]*array[1]**rnd()

def main(tick):
    pass

if __name__ == "__main__":
    main()