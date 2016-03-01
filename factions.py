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
                SUM(Object.keys(storage.goods).reduce(function(a,b){return a+(storage.goods[b]||0)},0)) AS goodsTotal\
            FROM massive\
            WHERE object == 'colony' && faction == '" + _id + "'\
            GROUP BY object\
            LIMIT 0, 99")
        if int(r['hits']) == 0:
            r = cp.query(payload="DELETE massive['" + _id + "']")['results'][0]['_id']
            return 'factions: disband faction ' + str(r)
        else:
            f = r['results'][0]
            population_industry = f['population'] / (f['population'] + f['industry'])
            growth_expand = (f['population'] + f['industry'] - f['colonies']) / (f['population'] + f['industry'])
            r = cp.query(payload="\
                UPDATE massive['" + _id + "']\
                SET approx['population_industry'] = "+str(population_industry)+",\
                    approx['growth_expand'] = "+str(growth_expand)+"")['results'][0]['_id']
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
                    'defence_attack': utils.dist_flat(config['defence_attack']),
                    'growth_expand': utils.dist_flat(config['growth_expand']),
                },
                'approx': {
                    'population_industry': 0.5,
                    'pacific_militaristic': 0.5,
                    'defence_attack': 0.5,
                    'growth_expand': 0.5,
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