def main(tick):
	if tick % 10 == 0:
	    for colony in get_all_colonies():
	        produce_goods(colony)  # Colony produce (10 * (habitability-population/10)) local goods per population
	        produce_materials(colony)  # Colony produce (10 * richness * weight) every material per industry
	        upkeep_population(colony)  # Colony upkeeps 1 unique exotic good or 4 local goods per population
	        upkeep_industry(colony)  # Colony upkeeps 1 unique exotic good or 4 solids per industry

if __name__ == "__main__":
    main()