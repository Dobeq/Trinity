import requests, json, time, math
from enum import Enum
from scrape import *

def setGlobals():
    global startSet
    global calls
    startSet = time.time()
    calls = 0

def rateLimit(func):
    def wrapper(*args, **kwargs):
        global startSet
        global calls
        if startSet + 1 < time.time():
            calls = 0
            startSet = time.time()
        else:
            calls += 1
            if calls >= 3:
                print('slow down!')
                time.sleep(startSet + 1 - time.time())
                startSet = time.time()
                calls = 0
        return func(*args, **kwargs)
    return wrapper

def timeDiff(time1, time2):
    if time1.tm_year!=time2.tm_year:
        return 4
    elif time1.tm_mon != time2.tm_mon:
        return 3
    elif abs(time1.tm_yday-time2.tm_yday) > 7:
        return 2
    elif time1.tm_mday != time2.tm_mday:
        return 1
    return 0

def ISOtoPy(thing):
    return time.strptime(thing,'%Y-%m-%dT%H:%M:%S.000+00:00')

@rateLimit
def getItem(item, head, header):
    if item == 'forma_blueprint':
        return 0
    if 'kavasa' in item:
        if 'buckle' in item:
            item = 'kavasa_prime_collar_buckle'
        elif 'band' in item:
            item = 'kavasa_prime_collar_band'
        elif 'blueprint' in item:
            item = 'kavasa_prime_collar_blueprint'
    if 'silva' in item:
        split = item.split('&')
        item = split[0] + 'and' + split[1]
    request = requests.get(head+'items/'+item+'/orders', headers=header)
    thing = request.json()['payload']['orders']
    filtered = list(filter(lambda x: x['order_type']=='buy', thing))
    filtered = list(filter(lambda x: timeDiff(ISOtoPy(x['creation_date']), time.gmtime())<=1, filtered))
    filtered = list(filter(lambda x: x['region'] == 'en', filtered))
    filtered.sort(key=lambda y: y['platinum'], reverse=True)
    if len(filtered) >= 1:
        return int(filtered[0]['platinum'])
    else:
        return 0

@rateLimit
def getAllItems(head, header):
    items = requests.get(head+'items', headers=header)
    itemList = []
    for item in items.json()['payload']['items']:
        itemList.append(item['url_name'])
    return itemList

@rateLimit
def getItemInfo(item, head, header):
    request = requests.get(head + 'items/' + item)
    return request.json()['payload']['item']

@rateLimit
def checkPrice(relics, head, header):
    output = []
    items = {}
    for relic in relics:
        if relic['name'] == 'axi_p1_relic':
            print('axi p1!')
        info = {'name':relic['name']}
        c = relic['common']
        u = relic['uncommon']
        r = relic['rare']
        d = relic['drops']
        intactChances = [.2533*3, .11*2, .02]
        exceptionalChances = [.2333*3, .13*2, .04]
        flawlessChances = [.2*3, .17*2, .06]
        radiantChances = [.1677*3, .2*2, .1]
        chances = [intactChances, exceptionalChances, flawlessChances, radiantChances]
        platTotals = [0, 0, 0]
        ev = [0, 0, 0, 0]
        for item in d:
            if item in c:
                slot = 0
            if item in u:
                slot = 1
            if item in r:
                slot = 2
            if item in items.keys():
                price = items[item]
            else:
                price = getItem(item, head, header)
                items[item] = price
            platTotals[slot] += price
        for i in range(4):
            for j in range(3):
                ev[i] += platTotals[j] * chances[i][j]
            ev[i] = round(ev[i], 3)
        info['ev'] = ev
        output.append(info)
    output.sort(key=lambda x:x['ev'][0], reverse=True)
    with open('relics.txt', 'w+') as f:
        jitems = json.dumps(items)
        f.write(jitems + '\n')
        for line in output:
            jline = json.dumps(line)
            f.write(jline + '\n')
        f.flush()
    return output


if __name__ == "__main__":
    head = 'https://api.warframe.market/v1/'
    header = {'platform':'pc', 'language':'en'}
    setGlobals()
    scan = input('rescan? [y]/n ' + '\n')
    if scan == 'y':
        relics = scrapeRelicRewards()
        prices = checkPrice(relics, head, header)
    missions = input('recheck missions? [y]/n ' + '\n')
    if missions == 'y':
        scrapeMissionRewards()
