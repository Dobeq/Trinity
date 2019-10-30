
import requests, re, json
import lxml.html as lh

def scrapeRelicRewards():
    url = 'http://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html'
    page = requests.get(url)
    doc = lh.fromstring(page.content)
    header = doc.xpath('/html/body/h3[@id="relicRewards"]')[0]
    table = header.xpath('following::table[1]')[0]
    rows = table.xpath('./tr[not(@class)]/*')
    relicI = 0
    relics = []
    while relicI < len(rows):
        data = list(map(lambda x: x.text_content(), rows[relicI:relicI + 13]))
        relicI += 52
        common = '(25.33%)'
        uncommon = '(11.00%)'
        rare = '(2.00%)'
        relic = {'name':"_".join(data[0].lower().split(" ")[:3]),
                      'drops':[], 'common':[], 'uncommon':[], 'rare':[]}
        for i in range(6):
            drop = data[2*i+1:2*i+3]
            cut = ['systems', 'chassis', 'neuroptics', 'wings', 'harness']
            if drop[0].lower().split(" ")[-2] in cut:
                url = "_".join(drop[0].lower().split(" ")[:-1])
            else:
                url = "_".join(drop[0].lower().split(" "))
            relic['drops'].append(url)
            rarity = drop[1].split(" ")[1]
            if rarity == common:
                relic['common'].append(url)
            elif rarity == uncommon:
                relic['uncommon'].append(url)
            elif rarity == rare:
                relic['rare'].append(url)
        relics.append(relic)
    return relics


def missionValue(mission):
    ev = 0
    if mission['type'] == 'survival':
        ev = mission['tiers'][0]['ev'][0] * 6 + mission['tiers'][1]['ev'][0] * 3 + mission['tiers'][2]['ev'][0] * 3
    if mission['type'] == 'interception':
        ev = mission['tiers'][0]['ev'][0] * 6 + mission['tiers'][1]['ev'][0] * 3 + mission['tiers'][2]['ev'][0] * 3
    if mission['type'] == 'defense':
        ev = mission['tiers'][0]['ev'][0] * 6 + mission['tiers'][1]['ev'][0] * 3 + mission['tiers'][2]['ev'][0] * 3
    if mission['type'] == 'excavation':
        ev = mission['tiers'][0]['ev'][0] * 24 + mission['tiers'][1]['ev'][0] * 12 + mission['tiers'][2]['ev'][0] * 12
    if mission['type'] == 'infested salvage':
        ev = mission['tiers'][0]['ev'][0] * 14 + mission['tiers'][1]['ev'][0] * 7 + mission['tiers'][2]['ev'][0] * 7
    if mission['type'] == 'spy':
        ev = (mission['tiers'][0]['ev'][0] + mission['tiers'][1]['ev'][0] + mission['tiers'][2]['ev'][0]) * 20
    if mission['type'] == 'disruption':
        ev = mission['tiers'][1]['ev'][0] * 2 + mission['tiers'][2]['ev'][0]
    if mission['type'] == 'rush':
        ev = (mission['tiers'][0]['ev'][0] + mission['tiers'][1]['ev'][0] + mission['tiers'][2]['ev'][0]) * 30
    if mission['type'] == 'sabotage':
        ev = (mission['tiers'][0]['ev'][0]) * 12
    if mission['type'] == 'mobile defense':
        ev = (mission['tiers'][0]['ev'][0]) * 8
    if mission['type'] == 'exterminate':
        ev = (mission['tiers'][0]['ev'][0]) * 15
    if mission['type'] == 'capture':
        ev = (mission['tiers'][0]['ev'][0]) * 30
    if mission['type'] == 'defection':
        ev = mission['tiers'][0]['ev'][0] * 8 + mission['tiers'][1]['ev'][0] * 4 + mission['tiers'][2]['ev'][0] * 4
    return ev

def scrapeMissionRewards():
    url = 'http://n8k6e2y6.ssl.hwcdn.net/repos/hnfvc0o3jnfvc873njb03enrf56.html'
    page = requests.get(url)
    doc = lh.fromstring(page.content)
    header = doc.xpath('/html/body/h3[@id="missionRewards"]')[0]
    table = header.xpath('following::table[1]')[0]
    rows = table.xpath('./tr/*')
    missions = []
    mission = {}
    tier = {}
    reward = []
    num = 0
    rank = 0
    for row in rows:
        if row.tag == 'th':
            if 'Rotation' not in row.text_content():
                if len(mission.keys()) > 0:
                    missions.append(mission)
                    num += 1
                mission = {}
                reward = []
                currTier = -1
                start = row
                mission['name'] = " ".join(row.text_content().split(" ")[:-1])
                mission['type'] = re.search('\(.*\)', row.text_content()).group()[1:-1].lower()
                mission['tiers'] = []
            else:
                currTier += 1
                rank = row.text_content().split(" ")[1]
                tier = {'rank': rank, 'rewards':[], 'ev':[0, 0, 0, 0]}
                mission['tiers'].append(tier)
        else:
            if currTier == -1:
                tier = {'rank': 'Total', 'rewards': [], 'ev':[0, 0, 0, 0]}
                mission['tiers'].append(tier)
                currTier = 0
            if len(reward) == 0:
                reward.append(row.text_content())
            else:
                reward.append(re.search('\(.*\)', row.text_content()).group()[1:-1])
                mission['tiers'][currTier]['rewards'].append(reward)
                reward = []

    with open('relics.txt', 'r') as f:
        lines = f.readlines()
        prices = json.loads(lines[0])
        for mission in missions:
            for tier in mission['tiers']:
                for reward in tier['rewards']:
                    url = "_".join(reward[0].lower().split(" "))
                    for line in list(map(json.loads, lines[1:])):
                        if line['name'] == url:
                            for i in range(len(line['ev'])):
                                tier['ev'][i] += round(line['ev'][i] * float(reward[1][:-1])/100, 3)
            mission['value'] = missionValue(mission)
    missions.sort(key=lambda x: missionValue(x), reverse=True)
    with open('missions.txt', 'w+') as f:
        for mission in missions:
            f.write(json.dumps(mission) + "\n")
if __name__ == '__main__':
    scrapeMissionRewards()