def main(tick):
	if tick % 50 == 0:
	    for faction in get_all_factions():
	        for colony in faction.colonies:
	            upgrade_colony(colony, faction)  # Colony upgrades either population or industry by 1000 local goods and 1000 solids
	            create_ships(colony, faction)  # Prioritize randomly weighted by preferences of Faction

if __name__ == "__main__":
    main()