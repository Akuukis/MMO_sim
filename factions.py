import re
from pprintpp import pprint as pp

import cp
import utils

def main(tick, config, q):
    count = int(cp.query(payload="SELECT * FROM massive WHERE object == 'faction' LIMIT 0, 0")['hits'])
    want = int(config['factions'])

    # Disband 'empty' factions with no colonies
    def update(_id):
        r = cp.query(payload="\
            SELECT\
                COUNT() as colonies,\
                SUM(population) AS population,\
                SUM(industry) AS industry,\
                SUM(storage.goods[goods]) AS goodsLocal,\
                SUM(Object.keys(storage.goods).reduce(function(a,b){return a+(storage.goods[b]||0)},0)) AS goodsTotal,\
                SUM(storage['troops']) AS troops,\
                SUM(storage['solids']) AS solids,\
                SUM(storage['metals']) AS metals,\
                SUM(storage['isotopes']) AS isotopes\
            FROM massive\
            WHERE object == 'colony' && faction == '" + _id + "'\
            GROUP BY object\
            LIMIT 0, 99")
        if int(r['hits']) == 0:
            r = cp.query(payload="DELETE massive['" + _id + "']")['results'][0]['_id']
            return 'factions: disband faction ' + str(r)
        else:
            troopsValue = config['troops'][0]+config['troops'][1]+config['troops'][2]+config['troops'][3]
            f = r['results'][0]
            colonyValue = (config['popUpgradeGoods']+config['popUpgradeSolids']+config['indUpgradeGoods']+config['indUpgradeSolids'])/2
            pacific = 1 + f['goodsTotal'] + f['solids'] + (f['population'] + f['industry']) * colonyValue
            military = 1 + f['metals'] + f['isotopes'] + f['troops'] * troopsValue
            defence = 1
            offence = 1

            r = cp.query(payload="\
                SELECT\
                    GROUP_KEY() AS type,\
                    COUNT() AS count,\
                    SUM(\
                        cargo['solids']+\
                        Object.keys(cargo.goods).reduce(function(a,b){return a+(cargo.goods[b]||0)},0)\
                        ) AS cargoPacific,\
                    SUM(\
                        cargo['metals']+\
                        cargo['isotopes']+\
                        cargo['troops']*" + str(troopsValue) + "\
                        ) AS cargoMilitary\
                FROM massive\
                WHERE object == 'ship' && faction == '" + _id + "'\
                GROUP BY type\
                LIMIT 0, 99")
            population_industry = f['population'] / (f['population'] + f['industry'])
            growth_expand = (f['population'] + f['industry'] - f['colonies']) / (f['population'] + f['industry'])
            if int(r['hits']) > 0:
                for ship in r['results']:
                    s = config['ships'][ship['type']]
                    pacific  += ship['cargoPacific']
                    pacific  += ship['count'] * (s[0]+s[1]+s[2]+s[3]) * (s[8]+s[9*colonyValue]) / (s[5]+s[8]+s[9*colonyValue])
                    military += ship['cargoMilitary']
                    military += ship['count'] * (s[0]+s[1]+s[2]+s[3]) * (s[5])                  / (s[5]+s[8]+s[9*colonyValue])
                    defence  += ship['count'] * s[4]
                    offence  += ship['count'] * s[5]

            r = cp.query(payload="\
                UPDATE massive['" + _id + "']\
                SET approx['population_industry'] = "+str(population_industry)+",\
                    approx['growth_expand'] = "+str(growth_expand)+",\
                    approx['pacific_militaristic'] = "+str(pacific/(pacific+military))+",\
                    approx['defence_offence'] = "+str(defence/(defence+offence))+",\
                    approx['pacific'] = "+str(pacific)+",\
                    approx['military'] = "+str(military)+"")['results'][0]['_id']
            return 'factions: update faction ' + str(r)

    def list_update():
        factions = cp.query(payload="\
            SELECT _id\
            FROM massive\
            WHERE object == 'faction'\
            ORDER BY Math.random()\
            LIMIT 0,"+str(max(1, round(want/config['beatFactions']))))
        if 'results' in factions:
            for faction in factions['results']:
                utils.queue(update, faction['_id'])
            return 'factions: listed '+str(len(factions['results']))+' faction(s) for updating'
        return 'factions: listing failed. No factions?'
    utils.queue(list_update)

    # Spawn new factions with initial colony
    def spawn(n):
        occupied = cp.query(payload="\
            SELECT SUM(population+industry) as size\
            FROM massive\
            WHERE object == 'colony' && anchor == '"+planet[n]['_id']+"'\
            GROUP BY anchor")
        if int(occupied['hits']) == 0 or (planet[n]['size'] >= occupied['results'][0]['size'] + 2):
            utils.queue(cp.put, payload={
                'object': 'faction',
                'flexibility': utils.dist_flat(config['flexibility']),
                'pref': {  # preferred optimal ratio between two, 0 prefers first, 1 prefers last, 0.5 is balanced.
                    'population_industry': utils.dist_flat(config['population_industry']),
                    'pacific_militaristic': utils.dist_flat(config['pacific_militaristic']),
                    'defence_offence': utils.dist_flat(config['defence_offence']),
                    'growth_expand': utils.dist_flat(config['growth_expand']),
                },
                'approx': {
                    'population_industry': 0.5,
                    'pacific_militaristic': 0.99,
                    'defence_offence': 0.5,
                    'growth_expand': 0.5,
                    'pacific': (config['initPop']+config['initInd'])*1000 + config['initGoodsLocal'] + config['initGoodsGenesis'] + config['initSolids'],
                    'military': config['initMetals'] + config['initIsotopes'],
                }},
                params='[faction'+str(tick)+'-'+str(n)+']',
                msg='factions: add faction'+str(tick)+'-'+str(n)
            )
            utils.queue(cp.put, payload={
                'object': 'colony',
                'faction': 'faction'+str(tick)+'-'+str(n),
                'anchor': planet[n]['_id'],
                'goods': re.search("(\w*)p", planet[n]['_id']).group(1),
                'untilJoins': {
                    'size': planet[n]['size'],
                    'habitability': planet[n]['habitability'],
                    'richness': planet[n]['richness'],
                    'materials': planet[n]['materials'],
                },
                'population': config['initPop'],
                'industry': config['initInd'],
                'storage': {
                    'goods': {
                        re.search("(\w*)p", planet[n]['_id']).group(1): config['initGoodsLocal'],
                        'genesis': config['initGoodsGenesis'],
                    },
                    'solids': config['initSolids'],  # Upkeep for industry
                    'metals': config['initMetals'],  # For structure of skips
                    'isotopes': config['initIsotopes'],  # For guns of ships
                    'ammo': 0  # For guns to shoot
                }},
                params='[colony'+str(tick)+'-'+str(tick)+'-'+str(n)+']',
                msg='factions: spawn colony'
            )
            return 'factions: spawn faction'+str(tick)+'-'+str(n)

    if want > count:
        planet = cp.query(payload="\
            SELECT _id, size, habitability, richness, materials\
            FROM massive\
            WHERE\
                object == 'planet' &&\
                type != 'Gas' &&\
                system_coords.radius < "+str(int(config['optimalDistance'][0]*config['optimalDistance'][1]))+" &&\
                system_coords.radius > "+str(int(config['optimalDistance'][0]/config['optimalDistance'][1]))+"\
            ORDER BY Math.abs("+str(config['optimalDistance'][0])+" - system_coords.radius) * Math.random()\
            LIMIT 0, "+str(max(1, round((want - count)/config['beatFactions'])))
            )["results"]
        for n in range(0, max(1, round((want - count)/config['beatFactions']))):
            spawn(n)

    return 'done'

if __name__ == "__main__":
    main()