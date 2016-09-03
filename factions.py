import re

import cp
import utils

def main(tick, config, q):
    count = int(cp.query(payload="SELECT * FROM massive WHERE object == 'faction' LIMIT 0, 0")['hits'])
    want = int(config['factions'])

    # Disband 'empty' factions with no colonies
    def disband(_id):
        r = cp.query(payload="SELECT *\
            FROM massive\
            WHERE object == 'colony' && faction == '" + _id + "'\
            LIMIT 0, 0")
        if int(r['hits']) == 0:
            r = cp.query(payload="DELETE massive['" + _id + "']")['results'][0]['_id']
            return 'factions: disband faction ' + str(r)
        else:
            return 'factions: keep faction ' + _id

    def list_disband():
        factions = cp.query(payload="\
            SELECT _id\
            FROM massive\
            WHERE object == 'faction'\
            ORDER BY Math.random()\
            LIMIT 0,"+str(max(1, round(want/config['cleanFactions']))))
        if 'results' in factions:
            for faction in factions['results']:
                utils.queue(disband, faction['_id'])
            return 'factions: listed '+str(len(factions['results']))+' factions for disbanding'
        return 'factions: listing failed. No factions?'
    utils.queue(list_disband)

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
                'pref': {  # 0 prefers first, 1 prefers last, 0.5 is indifferent.
                    'population_industry': utils.dist_flat(config['population_industry']),
                    'pacific_militaristic': utils.dist_flat(config['pacific_militaristic']),
                    'defence_attack': utils.dist_flat(config['defence_attack']),
                    'growth_expand': utils.dist_flat(config['growth_expand']),
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