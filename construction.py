import cp
import utils
# from pprintpp import pprint as pp

def main(tick, config, q):
    def construct(f, c):
        # pp(f)
        # pp(c)
        factionId = f['_id']
        colonyId = c['_id']
        flex = float(f['flexibility'])
        prefPM = float(f['pref']['pacific_militaristic'])
        prefDO = float(f['pref']['defence_offence'])
        prefGE = float(f['pref']['growth_expand'])
        prefPI = float(f['pref']['population_industry'])
        apprPM = float(f['approx']['pacific_militaristic'])
        apprDO = float(f['approx']['defence_offence'])
        apprGE = float(f['approx']['growth_expand'])
        apprPI = float(f['approx']['population_industry'])
        population = int(c['population'])
        industry = int(c['industry'])
        goodsl = int(c['storage']['goods'][c['goods']])
        solids = int(c['storage']['solids'])
        metals = int(c['storage']['metals'])
        isotopes = int(c['storage']['isotopes'])
        troops = int(c['storage']['troops'])

        # y = x * (k-cx)
        # y = -cxx + kx
        # 0 = k - 2cx
        # 0 = habitability - 2*DAR*x
        # habitability = 2*DAR*x
        # x = habitability / (2*DAR)
        maxPop = max(1, min(int(c['untilJoins']['size'])-industry, int( c['untilJoins']['habitability']/(config['popDAR']*2) )))
        maxInd = max(1, min(int(c['untilJoins']['size'])-population, int( c['untilJoins']['richness']/(config['indDAR']*2) )))

        cargo = {
            'goods': { 'genesis': 0 },
            'solids': 0,  # Upkeep for industry
            'metals': 0,  # For structure of skips
            'isotopes': 0,  # For guns of ships
            'troops': 0,  # For defence and conquer
            'ammo': 0  # For guns to shoot
        }

        # Military
        #         -- global [0; inf) -- * ------- local [0; inf) ------- * - local [0; inf) -
        trooper  = (1-prefPM)/(1-apprPM) * (population+industry)/(prefDO) / troops # troops always should be around 1.00
        frigate = (1-prefPM)/(1-apprPM) * (  prefDO)/(  apprDO)          * metals/isotopes
        striker = (1-prefPM)/(1-apprPM) * (1-prefDO)/(1-apprDO)          * isotopes/metals

        # print("              military %.3f, %.3f, %.3f" % (trooper, frigate, striker))
        # P.S. If no resources, then hoard and wait.
        if   trooper  == max(trooper, frigate, striker):
            t = config['troops']
            if goodsl > t[0] and solids > t[1] and metals > t[2] and isotopes > t[3]:
                goodsl -= t[0]
                solids -= t[1]
                metals -= t[2]
                isotopes -= t[3]
                troops += 1
                print('              construction: add trooper in colony ' + colonyId + ' of ' + factionId)
        elif frigate == max(trooper, frigate, striker):
            s = config['ships']['frigate']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn frigate
                utils.queue(cp.put, payload={
                        "object": "ship",
                        "faction": factionId,
                        "system_coords": [0,0,0],  # TODO
                        "type": "frigate",
                        "cargo": cargo
                    },
                    msg='construction: spawn ship frigate for ' + factionId
                )
        elif striker == max(trooper, frigate, striker):
            s = config['ships']['striker']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn striker
                utils.queue(cp.put, payload={
                        "object": "ship",
                        "faction": factionId,
                        "system_coords": [0,0,0],  # TODO
                        "type": "striker",
                        "cargo": cargo
                    },
                    msg='construction: spawn ship striker for ' + factionId
                )
        else:
            pass  # Error!

        # Pacific
        #         -- global [0; inf) -- * -- global [0; inf) -- * -- global [0; inf) -- * ------- local [0; 2] --------  ---------------- local [0; inf] ----------------
        pop     = (  prefPM)/(  apprPM) * (1-prefGE)/(1-apprGE) * (1-prefPI)/(1-apprPI) * 2*(maxPop - population)/maxPop
        ind     = (  prefPM)/(  apprPM) * (1-prefGE)/(1-apprGE) * (  prefPI)/(  apprPI) * 2*(maxInd - industry  )/maxInd
        settler = (  prefPM)/(  apprPM) * (  prefGE)/(  apprGE)  # Settler always should be around 1.00
        trader  = (  prefPM)/(  apprPM) *                                                        max(0, (solids - goodsl)/config['ships']['trader'][1])

        # print("              pacific  %.3f, %.3f, %.3f, %.3f" % (pop, ind, settler, trader))
        # P.S. If no resources, then hoard and wait.
        if   pop     == max(pop, ind, settler, trader):
            if goodsl > config['popUpgradeGoods'] and solids > config['popUpgradeSolids']:
                goodsl -= config['popUpgradeGoods']
                solids -= config['popUpgradeSolids']
                population += 1
                print('              construction: upgrade population in colony ' + colonyId + ' of ' + factionId)
        elif ind     == max(pop, ind, settler, trader):
            if goodsl > config['indUpgradeGoods'] and solids > config['indUpgradeSolids']:
                goodsl -= config['indUpgradeGoods']
                solids -= config['indUpgradeSolids']
                industry += 1
                print('              construction: upgrade industry in colony ' + colonyId + ' of ' + factionId)
        elif settler == max(pop, ind, settler, trader):
            s = config['ships']['settler']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn settler
                utils.queue(cp.put, payload={
                        "object": "settler",
                        "faction": factionId,
                        "system_coords": [0,0,0],  # TODO
                        "type": "striker",
                        "cargo": cargo
                    },
                    msg='construction: spawn ship settler for ' + factionId
                )
        elif trader  == max(pop, ind, settler, trader):
            s = config['ships']['trader']
            if goodsl > s[0] and solids > s[1] and metals > s[2] and isotopes > s[3]:
                goodsl -= s[0]
                solids -= s[1]
                metals -= s[2]
                isotopes -= s[3]
                # Spawn trader
                utils.queue(cp.put, payload={
                        "object": "trader",
                        "faction": factionId,
                        "system_coords": [0,0,0],  # TODO
                        "type": "striker",
                        "cargo": cargo
                    },
                    msg='construction: spawn trader striker for ' + factionId
                )
        else:
            pass  # Error!

        # Update new resources
        r = cp.query(payload="\
            UPDATE massive['" + colonyId + "']\
            SET storage['goods']['"+c['goods']+"'] = "+str(goodsl)+",\
                storage['solids'] = "+str(solids)+",\
                storage['metals'] = "+str(metals)+",\
                storage['isotopes'] = "+str(isotopes)+",\
                storage['troops'] = "+str(troops)+",\
                population = "+str(population)+",\
                industry = "+str(industry)+"\
        ")['results'][0]['_id']
        return 'construction: update colony '+r+' of ' +factionId

    def perColony(faction):
        colonies = cp.query(payload="\
            SELECT goods, storage, industry, population, untilJoins\
            FROM massive\
            WHERE\
                object == 'colony' && \
                faction == '"+faction['_id']+"'")
        if int(colonies['hits']) > 0:
            for colony in colonies['results']:
                utils.queue(construct, faction, colony)
        return 'construction: for '+faction['_id']+' construct in all '+str(colonies['hits'])+' colonies'

    # Whom construction should happen this tick?
    r = cp.query(payload="\
        SELECT flexibility, pref, approx FROM massive\
        WHERE object == 'faction' && Math.random()<"+str(1/config['beatConstruction'])+"\
        LIMIT 0, 999999")

    if int(r['hits']) > 0:
        for lucky in r['results']:
            utils.queue(perColony, lucky)
    return 'construction: done'

if __name__ == "__main__":
    main()