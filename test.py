#!/usr/bin/python3.4

import requests
from pprintpp import pprint as pp

# Clusterpoint connection data
host = "192.168.7.58"
username = "root"
password = "password"
port = "5580"
path = "v4/1/massive"
url = "http://" + host + ":" + port + "/" + path

def post(url, payload, msg=None, errorMsg=None):
    r = requests.post(url, json=payload, auth=(username, password)).json()
    if not r['error']:
        if msg:
            print(msg)
    else:
        pp(r)
        if errorMsg:
            print(errorMsg)
    return r

def query(url, payload, msg=None, errorMsg=None):
    r = requests.post(url + '/_query', data=payload, auth=(username, password)).json()
    if not r['error']:
        if msg:
            print(msg)
    else:
        pp(r)
        if errorMsg:
            print(errorMsg)
    return r

# Manual query below

pp(query(url,"SELECT GROUP_KEY() as distance, COUNT() FROM massive WHERE type == 'planet' GROUP BY Math.floor(distance/50)*50 ORDER BY distance ASC LIMIT 0,10"))