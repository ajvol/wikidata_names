#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request, urllib.response
from collections import defaultdict
import json
import re

__author__ = 'Ajvol'

def get_ru_labels(ids, q):
    # https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q42|Q1&props=labels&languages=ru
    url_ru_labels = 'https://www.wikidata.org/w/api.php?format=json&action=wbgetentities&ids='+ids+'&props=labels&languages=ru'
    response = urllib.request.urlopen(url_ru_labels)
    str_response = response.readall().decode('utf-8')
    item_json = json.loads(str_response)

    ru_labels = []
    for ent in item_json["entities"]:
        try:
            ru_labels.append(item_json["entities"][ent]["labels"]["ru"]["value"])
        except:
            ''

    try:
        existing_title = item_json["entities"][q]["labels"]["ru"]["value"]
        ru_labels.remove(existing_title)
    except:
        existing_title = ''

    return (existing_title, ru_labels)

#labels = ['Зоммер, Янн', 'Тьерсен, Ян', 'Нотра, Ян', 'Ян ЛеКун', 'Янн М’Вила', 'Ян Бон Артюс-Бертран', 'Кеффелек, Ян', 'Бёрон, Ян', 'Капе, Ян', 'Мартел, Янн', 'Ле Гак, Ян']
#print(get_ru_name(labels))
def get_ru_name(labels):
    if len(labels) <= 1:
        return ''

    candidates = defaultdict(int)

    for label in labels:
        label =  re.sub('(.*), ', '', label)
        label = label.split(' ')[0]
        candidates[label] += 1

    sorted_cans = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    print(sorted_cans)

    res = ''
    uniques_num = len(sorted_cans)

    if uniques_num == 1:
        k, v = sorted_cans[0]
        res = k

    if uniques_num >= 2:
        k1, v1 = sorted_cans[0]
        res = k1
        k2, v2 = sorted_cans[1]
        if v2 * 3 >= v1 and v2 > 1:
            res += ' / ' + k2
            if uniques_num >= 3:
                k3, v3 = sorted_cans[2]
                if v3 * 2 >= v2 and v3 > 1:
                    res += ' / ' + k2

    return res



###############################################################


qlist = [
    'Q7451984',   # (Seppo)	222 items link to this item
    'Q482154',    # (Amédée)	222 items link to this item
    'Q17596178',  # (Juliusz)	222 items link to this item
    'Q16277367',  # (Jerónimo)	222 items link to this item
    'Q13582327',  # (Dwight)	220 items link to this item
    'Q1476141',   # (Jaakko)	219 items link to this item
    'Q13564380'   # (Yann)	218 items link to this item
]

for q in qlist:
    print('--------')
    print(q)

    #url = "http://www.wikidata.org/w/api.php?format=json&action=wbgetentities&ids="+q+"&props=labels&languages=ru|en"

    # http://wdq.wmflabs.org/api?q=claim[735:7451984]%20AND%20link[ruwiki]
    url_what_have_this_name = 'http://wdq.wmflabs.org/api?q=claim[735:'+q.replace('Q','')+']%20AND%20link[ruwiki]'

    response = urllib.request.urlopen(url_what_have_this_name)
    str_response = response.readall().decode('utf-8')
    item_json = json.loads(str_response)

    ids = q
    for i in item_json["items"]:
        ids += '|Q'+str(i)

    print(ids)

    existing_title, ru_labels = get_ru_labels(ids, q)

    print(existing_title)
    print(ru_labels)
    print(get_ru_name(ru_labels))

