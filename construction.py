def main(tick, config, q):
    return  # Drafted, TODO

    def construct(f, c):
        flex = f['flexibility']
        prefPM = f['pref']['pacific_militaristic']
        prefDO = f['pref']['defence_offence']
        prefGE = f['pref']['growth_expand']
        prefPI = f['pref']['population_industry']
        apprPM = f['approx']['pacific_militaristic']
        apprDO = f['approx']['defence_offence']
        apprGE = f['approx']['growth_expand']
        apprPI = f['approx']['population_industry']
        c['untilJoins']['size']
        c['untilJoins']['habitability']
        c['untilJoins']['richness']
        population = c['population']
        industry = c['industry']
        goodsl = c['storage']['goods'][c['goods']]
        solids = c['storage']['solids']
        metals = c['storage']['metals']
        isotopes = c['storage']['isotopes']
        troops = c['storage']['troops']

        maxPop = c['untilJoins']['habitability']/(config['popDAR']*2)
        maxInd = c['untilJoins']['richness']/(config['indDAR']*2)

        # Military
        #         -- global [0; inf) -- * ------- local [0; inf) ------- * - local [0; inf) -
        troops  = (1-prefPM)/(1-apprPM) * (population+industry)/(prefDO)  # troops always should be around 1.00
        frigate = (1-prefPM)/(1-apprPM) * (  prefDO)/(  apprDO)          * metals/isotopes
        striker = (1-prefPM)/(1-apprPM) * (1-prefDO)/(1-apprDO)          * isotopes/metals

        # P.S. If no resources, then save and wait.
        if   troops  == max(troops, frigate, striker):
            t = config['troops']
            if goodsl > t[0] and solids > t[1] and metals > t[2] and isotopes > t[3]:
                goodsl -= t[0]
                solids -= t[1]
                metals -= t[2]
                isotopes -= t[3]
                troops += 1
        elif frigate == max(troops, frigate, striker):
            s = config['ships']['frigate']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn frigate
        elif striker == max(troops, frigate, striker):
            s = config['ships']['striker']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn striker
        else:
            pass  # Error!

        # Pacific
        #         -- global [0; inf) -- * -- global [0; inf) -- * -- global [0; inf) -- * ------- local [0; 2] --------  ---------------- local [0; inf] ----------------
        pop     = (  prefPM)/(  apprPM) * (1-prefGE)/(1-apprGE) * (1-prefPI)/(1-apprPI) * 2*(maxPop - population)/maxPop
        ind     = (  prefPM)/(  apprPM) * (1-prefGE)/(1-apprGE) * (  prefPI)/(  apprPI) * 2*(maxInd - industry  )/maxInd
        settler = (  prefPM)/(  apprPM) * (  prefGE)/(  apprGE)  # Settler always should be around 1.00
        trader  = (  prefPM)/(  apprPM) *                                                        max(0, (solids - goodsl)/config['ships']['trader'][1])

        # P.S. If no resources, then save and wait.
        if   pop     == max(pop, ind, settler, trader):
            if goodsl > config['popUpgradeGoods'] and solids > config['popUpgradeSolids']:
                goodsl -= config['popUpgradeGoods']
                solids -= config['popUpgradeSolids']
                population += 1
        elif ind     == max(pop, ind, settler, trader):
            if goodsl > config['indUpgradeGoods'] and solids > config['indUpgradeSolids']:
                goodsl -= config['indUpgradeGoods']
                solids -= config['indUpgradeSolids']
                industry += 1
        elif settler == max(pop, ind, settler, trader):
            s = config['ships']['settler']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn settler
        elif trader  == max(pop, ind, settler, trader):
            s = config['ships']['trader']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn trader
        else:
            pass  # Error!

        # Update new resources

    def perColony(faction):
        colonies = cp.query(payload="\
            SELECT goods, storage, industry, population, untilJoins\
            FROM massive\
            WHERE faction == '"+faction['_id']+"'")
        if int(colonies['hits']) > 0:
            for colony in colonies['results']:
                utils.queue(construct, faction, colony)
        return 'construction: for '+faction['_id']+' construct in all '+str(colonies['hits'])+' colonies'

    # Whom construction should happen this tick?
    r = cp.query(payload="\
        SELECT flexibility, pref, approx FROM massive\
        WHERE object == 'faction' &&\
            Math.random()<"+str(1/config['batchConstruction']/config['beatConstruction'])+"\
        LIMIT 0, 999999")

    if int(r['hits']) > 0:
        for lucky in r['results']:
            utils.queue(perColony, lucky)
    return 'construction: done'

if __name__ == "__main__":
    main()