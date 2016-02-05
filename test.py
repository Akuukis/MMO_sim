#!/usr/bin/python3.4

from pprintpp import pprint as pp
import cp

# Manual query below

pp(cp.query(payload="SELECT GROUP_KEY() as distance, COUNT() FROM massive WHERE type == 'planet' GROUP BY Math.floor(distance/50)*50 ORDER BY distance ASC LIMIT 0,10"))