
import requests
import lxml.html as lh

def scrape():
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