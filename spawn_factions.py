
def main(tick):
    if random.random() > get_all_colonies().length / config.maxColonies:
        picklist = []
        for planet in get_all_planets():
            distance = get_vector(planet.coords, planet.sun.coords)
            moons = planet.moons.length
            # 8 minutes and 1 moon gives highest chance (like Earth)
            chance = moons / (moons * 2 + 0.0001)
            chance -= math.fabs(config.optimalPlanetDistance - distance) / config.optimalPlanetRange
            if chance > 0.01:
                picklist.append([chance, planet])

        lucky = choose_weighted(picklist)
        faction = spawn_faction()
        spawn_colony(faction, lucky)

if __name__ == "__main__":
    main()