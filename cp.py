
import requests
from pprintpp import pprint as pp

# Clusterpoint connection data
host = "192.168.7.58"
port = "5580"
path = "v4/1/massive/"
url = "http://" + host + ":" + port + "/" + path
username = "root"
password = "password"

def put(payload, params='', msg=None, errorMsg=None):
    r = requests.post(url + params, json=payload, auth=(username, password)).json()
    if not r['error']:
        if msg:
            print(msg)
    else:
        pp(r)
        if errorMsg:
            print(errorMsg)
    return r

def query(payload, msg=None, errorMsg=None):
    print(url)
    r = requests.post(url + '_query', data=payload, auth=(username, password)).json()
    if not r['error']:
        if msg:
            print(msg)
    else:
        pp(r)
        if errorMsg:
            print(errorMsg)
    return r