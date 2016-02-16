
import random
import json

import cp

def main(tick, config, q):
    # On average, per tick:
    # Colony produce (10 * (habitability-population/10)) local goods per population
    # Colony produce (10 * richness * weight) every material per industry
    # Colony upkeeps 1 unique exotic good or 4 local goods per population
    # Colony upkeeps 1 unique exotic good or 4 solids per industry
    def produce(_id):
        batch = 2 * config['batchEconomy']
        colony = cp.query(payload="\
            SELECT goods, storage, industry, population, untilJoins\
            FROM massive\
            WHERE _id == '"+_id+"'")['results'][0]

        # produce_goods
        goodsPerPop = float(colony['untilJoins']['habitability']) - float(colony['population']) * config['popDAR']
        goodsTotal = batch * float(colony['population']) * goodsPerPop
        colony['storage']['goods'][colony['goods']] += goodsTotal

        # produce_materials
        materialsPerInd = float(colony['untilJoins']['richness']) - float(colony['industry']) * config['indDAR']
        materialsTotal = batch * float(colony['industry']) * materialsPerInd
        colony['storage']['solids'] += materialsTotal * float(colony['untilJoins']['materials'][0])
        colony['storage']['metals'] += materialsTotal * float(colony['untilJoins']['materials'][1])
        colony['storage']['isotopes'] += materialsTotal * float(colony['untilJoins']['materials'][2])

        r = cp.query(payload="\
            UPDATE massive['" + _id + "']\
            SET storage.goods['"+colony['goods']+"'] = "+str(int(colony['storage']['goods'][colony['goods']]))+",\
                storage['solids'] = "+str(int(colony['storage']['solids']))+",\
                storage['metals'] = "+str(int(colony['storage']['metals']))+",\
                storage['isotopes'] = "+str(int(colony['storage']['isotopes']))+"\
        ")['results'][0]['_id']
        return 'economy: produce at ' + r

    def upkeep(_id):
        batch = 2 * config['batchEconomy']
        colony = cp.query(payload="\
            SELECT goods, storage, industry, population, untilJoins\
            FROM massive\
            WHERE _id == '"+_id+"'")['results'][0]

        # upkeep_population
        size = colony['population']
        for key, amount in colony['storage']['goods'].items():
            if colony['storage']['goods'][key] >= batch and random.random() >= config['popForeignGoods']:
                colony['storage']['goods'][key] -= batch
                size -= 1
                if size == 0:
                    break
        if colony['storage']['goods'][colony['goods']] >= size * config['popLocalPenalty'] * batch:
            colony['storage']['goods'][colony['goods']] -= size * config['popLocalPenalty'] * batch
        else:
            colony['population'] -= 1
            colony['storage']['goods'][colony['goods']] += config['popDowngradeRefund'] * config['popUpgradeGoods']
            colony['storage']['solids'] += config['popDowngradeRefund'] * config['popUpgradeSolids']

        # upkeep_industry
        size = colony['industry']
        for key, amount in colony['storage']['goods'].items():
            if colony['storage']['goods'][key] >= batch and random.random() >= config['indForeignGoods']:
                colony['storage']['goods'][key] -= batch
                size -= 1
                if size == 0:
                    break
        if colony['storage']['solids'] >= size * config['indLocalPenalty'] * batch:
            colony['storage']['solids'] -= size * config['indLocalPenalty'] * batch
        else:
            colony['industry'] -= 1
            colony['storage']['goods'][colony['goods']] += config['indDowngradeRefund'] * config['indUpgradeGoods']
            colony['storage']['solids'] += config['indDowngradeRefund'] * config['indUpgradeSolids']


        r = cp.query(payload="\
            UPDATE massive['" + _id + "']\
            SET storage['goods'] = "+json.dumps(colony['storage']['goods'])+",\
                storage['solids'] = "+str(int(colony['storage']['solids']))+",\
                storage['metals'] = "+str(int(colony['storage']['metals']))+",\
                storage['isotopes'] = "+str(int(colony['storage']['isotopes']))+",\
                population = "+str(int(colony['population']))+",\
                industy = "+str(int(colony['industry']))+"\
        ")['results'][0]['_id']
        return 'economy: upkeep at ' + r

    # Workaround for Python scoping
    def workaround_produce(_id):
        q.put(lambda a, b, c: produce(_id))
    def workaround_upkeep(_id):
        q.put(lambda a, b, c: upkeep(_id))

    # Whom production or upkeep should happen this tick?
    luckies = cp.query(payload="\
        SELECT _id FROM massive\
        WHERE object == 'colony' && Math.random()<"+str(1/config['batchEconomy'])+"\
        LIMIT 0, 999999")["results"]

    # Iterate through colonies
    for lucky in luckies:
        if random.random() < 0.5:
            workaround_produce(lucky['_id'])
        else:
            workaround_upkeep(lucky['_id'])

    return 'done'

if __name__ == "__main__":
    main()