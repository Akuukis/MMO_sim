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
pp(cp.query(payload="\
    SELECT\
      SUM(storage.solids) AS solids,\
      SUM(storage.metals) AS metals,\
      SUM(storage.isotopes) AS isotopes,\
      SUM(storage.goods[goods]) AS goodsLocal,\
      SUM(Object.keys(storage.goods).reduce(function(a,b){return a+(storage['goods'][b] || 0)},0)) AS goodsAll\
    FROM massive\
    WHERE object == 'colony'\
    GROUP BY object"))

# All objects in universe
pp(cp.query(payload="\
    SELECT\
      GROUP_KEY()[0] AS object,\
      COUNT() AS count\
    FROM massive\
    GROUP BY object\
    ORDER BY object ASC"))

# Last ticks and their length
pp(cp.query(payload="\
    SELECT\
      value,\
      last,\
      value-last AS length\
    FROM massive\
    WHERE object =='tick'\
    ORDER BY value DESC\
    LIMIT 0, 5"))

# Breakdown of colonies by habitability
pp(cp.query(payload="\
SELECT\
    untilJoins.habitability as hab,\
    AVG(population),\
    SUM(population),\
    COUNT(),\
    AVG(storage.goods[goods])\
    AVG(Object.keys(storage.goods).reduce(function(a,b){return a+(storage.goods[b]||0)},0)) as 'AVG(allGoods)'\
FROM massive\
WHERE object == 'colony'\
GROUP BY untilJoins.habitability\
ORDER BY hab\
LIMIT 0, 99"))