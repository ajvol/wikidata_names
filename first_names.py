#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request, urllib.response
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

print('ш я жх ё') # ru
print('š áč'.encode('cp1251','replace'))      # cz

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

    for label in ru_labels:
        label


'''





    if "en" in item_json["entities"][q]["labels"]:
        en_title = item_json["entities"][q]["labels"]["en"]["value"]
    else:
        en_title = ''

    if "ru" in item_json["entities"][q]["labels"]:
        ru_title = item_json["entities"][q]["labels"]["ru"]["value"]
    else:
        ru_title = ''

    response = urllib.request.urlopen(url_links_here)
    str_response = response.readall().decode('utf-8')
    item_json = json.loads(str_response)

    for

    print(en_title.encode('cp1251','replace'))
    print(ru_title.encode('cp1251','replace'))
'''