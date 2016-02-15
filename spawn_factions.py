def main(tick):

    faction = {
        'colonies': [colony, colony],
        'pref': {  # 0 prefers first, 1 prefers last, 0.5 is indifferent.
            'population_industry': 0.5,  # At what ratio (weighted by habitability and richness) to keep industry
            'pacific_militaristic': 0.5,  # Size of warfleet to keep
            'defence_attack': 0.5,  # Ratio of created warships to dedicate for defence
            'growth_expand': 0.5,  # At what % of optimalPopulation to grow further or create settler
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