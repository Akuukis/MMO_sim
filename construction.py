def main(tick, config, q):
    return  # Drafted, TODO

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


    if tick % 50 == 0:
        for faction in get_all_factions():
            for colony in faction.colonies:
                upgrade_colony(colony, faction)  # Colony upgrades either population or industry by 1000 local goods and 1000 solids
                create_ships(colony, faction)  # Prioritize randomly weighted by preferences of Faction

if __name__ == "__main__":
    main()