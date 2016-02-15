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


def main(tick, config, q):
    return  # Drafted, TODO


    item = {
        'type': 'ship' or 'part',
        'subtype': 123456789,  # id of model.
        'amount': 1
    }

    if tick % 10 == 0:
        for colony in get_all_colonies():
            produce_goods(colony)  # Colony produce (10 * (habitability-population/10)) local goods per population
            produce_materials(colony)  # Colony produce (10 * richness * weight) every material per industry
            upkeep_population(colony)  # Colony upkeeps 1 unique exotic good or 4 local goods per population
            upkeep_industry(colony)  # Colony upkeeps 1 unique exotic good or 4 solids per industry

if __name__ == "__main__":
    main()