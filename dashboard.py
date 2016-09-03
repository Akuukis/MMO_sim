#!/usr/bin/python3

from pprintpp import pprint as pp

import cp

# To delete all factions and colonies, use
#
# SELECT *
# FROM massive
# WHERE object == 'colony' || object == 'faction'
# LIMIT 0, 500

# All resources in universe
goods = cp.query(payload="\
    SELECT\
      SUM(storage.solids) AS solids,\
      SUM(storage.metals) AS metals,\
      SUM(storage.isotopes) AS isotopes,\
      SUM(storage.goods[goods]) AS goodsLocal,\
      SUM(Object.keys(storage.goods).reduce(function(a,b){return a+(Number(storage.goods[b]) || 0)},0)) AS goodsAll\
    FROM massive\
    WHERE object == 'colony'\
    GROUP BY object")['results'][0]

# All objects in universe
objectsRaw = cp.query(payload="\
    SELECT\
      GROUP_KEY()[0] AS object,\
      COUNT() AS count\
    FROM massive\
    GROUP BY object\
    ORDER BY object ASC")['results']

objects = {}
for o in objectsRaw:
    objects[o['object']] = int(o['count'])

# Last ticks and their length
n = 10
lastTicks = cp.query(payload="\
    SELECT\
      value,\
      last,\
      value-last AS length\
    FROM massive\
    WHERE object =='tick'\
    ORDER BY value DESC\
    LIMIT 0, "+str(n)+"")['results']

length = 0
for l in lastTicks:
    length += l['length']/n

# Breakdown of colonies by habitability
colonies = cp.query(payload="\
    SELECT\
        untilJoins.habitability as hab,\
        AVG(population),\
        SUM(population),\
        COUNT(),\
        AVG(storage.goods[goods])\
    FROM massive\
    WHERE object == 'colony'\
    GROUP BY untilJoins.habitability\
    ORDER BY hab\
    LIMIT 0, 99")['results']

print("               tick, length(tick): #%i, %.4fs"         % (objects['tick'], length))
print(" [systems, stars, planets, moons]: [%i, %i, %i, %i]"   % (objects['system'], objects['star'], objects['planet'], objects['moon'], ))
print("[factions, coloniesAll, goodsAll]: [%i, %i, %i]"       % (objects['faction'], objects['colony'], goods['goodsAll']))
print("       [solids, metals, isotopes]: [%.1f, %.1f, %.1f]" % (goods['solids']/objects['colony'], goods['metals']/objects['colony'], goods['isotopes']/objects['colony']))
print("    [goodsAll, goodsLocal], ratio: [%.1f, %.1f], %.3f" % (goods['goodsAll']/objects['colony'], goods['goodsLocal']/objects['colony'], goods['goodsLocal']/goods['goodsAll']))