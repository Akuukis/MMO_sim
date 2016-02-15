
import requests
import json
from jsmin import jsmin
from pprintpp import pprint as pp

# Create 'cp_config.json' from 'cp_config.json.example'
with open('cp_config.json') as data_file:
    con = json.loads(jsmin(data_file.read()))
url = "http://" + con['host'] + ":" + con['port'] + "/v4/" + str(con['userid']) + "/" + con['db']

def put(payload, params='', msg=None, errorMsg=None):
    r = requests.post(url + params, json=payload, auth=(con['username'], con['password'])).json()
    if not r['error']:
        if msg:
            return msg
    else:
        if errorMsg:
            return errorMsg
    return r

def query(payload, msg=None, errorMsg=None):
    r = requests.post(url + '/_query', data=payload, auth=(con['username'], con['password'])).json()
    if not r['error']:
        if msg:
            return msg
        else:
            return r
    else:
        if errorMsg:
            return errorMsg
        else:
            return False
