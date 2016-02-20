import re

import cp
import utils

def main(tick, config, q):
    # Delete 'empty' factions with no colonies
    pass  # TODO

    # Abandon depopulation colonies
    def abandon(_id):
        r = cp.query(payload="\
            UPDATE massive['" + _id + "']\
            SET faction = null",
            msg='economy: abandon colony '+_id)['results'][0]['_id']
        return 'economy: upkeep at ' + r

    def workaround_abandon(_id):
        q.put(lambda a, b, c: abandon(_id))

    colonies = cp.query(payload="\
        SELECT _id, faction\
        FROM massive\
        WHERE object == 'colony' && population == 0 && faction")
    if 'results' in colonies:
        for colony in colonies['results']:
            workaround_abandon(colony['_id'])

    # Spawn new factions with initial colony
    count = int(cp.query(payload="SELECT * FROM massive WHERE object == 'faction' LIMIT 0, 0")['hits'])
    want = int(utils.dist_skewedLeft(config['factions']))
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
            LIMIT 0, 1"
            )["results"][0]
        occupied = cp.query(payload="\
            SELECT SUM(population+industry) as size\
            FROM massive\
            WHERE object == 'colony' && anchor == '"+planet['_id']+"'\
            GROUP BY anchor")
        if int(occupied['hits']) == 0 or (planet['size'] >= occupied['results'][0]['size'] + 2):
            q.put(lambda a, b, c: cp.put(payload={
                'object': 'faction',
                'pref': {  # 0 prefers first, 1 prefers last, 0.5 is indifferent.
                    'population_industry': utils.dist_flat(config['population_industry']),
                    'pacific_militaristic': utils.dist_flat(config['pacific_militaristic']),
                    'defence_attack': utils.dist_flat(config['defence_attack']),
                    'growth_expand': utils.dist_flat(config['growth_expand']),
                }},
                params='[faction'+str(tick)+']',
                msg='Spawn faction '+str(tick)
            ))
            q.put(lambda a, b, c: cp.put(payload={
                'object': 'colony',
                'faction': 'faction'+str(tick),
                'anchor': planet['_id'],
                'goods': re.search("(\w*)p", planet['_id']).group(1),
                'untilJoins': {
                    'habitability': planet['habitability'],
                    'richness': planet['richness'],
                    'materials': planet['materials'],
                },
                'population': 1,
                'industry': 1,
                'storage': {
                    'goods': {
                        re.search("(\w*)p", planet['_id']).group(1): 100,
                    },
                    'solids': 100,  # Upkeep for industry
                    'metals': 0,  # For structure of skips
                    'isotopes': 0,  # For guns of ships
                    'ammo': 0  # For guns to shoot
                }},
                msg='Spawn colony'
            ))

if __name__ == "__main__":
    main()