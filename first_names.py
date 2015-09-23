#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request
import urllib.response
from collections import defaultdict
import json
import re
import requests

__author__ = 'Ajvol'
baseurl = 'https://www.wikidata.org/w/'


def get_q_list():
    # 202444 - личное имя
    # 12308941 - мужское
    # 11879590 - женское
    # 3409032 - юнисекс

    url = 'http://tools.wmflabs.org/wikidata-terminator/?list&lang=ru&mode=t1000&q=claim[31:202444,12308941,11879590,3409032]'
    url = 'http://tools.wmflabs.org/wikidata-terminator/?list&lang=ru&mode=t1000&q=claim[31:(claim[279:202444])]%20OR%20claim[31:202444]'
    response = urllib.request.urlopen(url)
    str_response = response.readall().decode('utf-8')

    q_list = re.findall("<tr><td><a href='//www.wikidata.org/wiki/(Q\d+?)'.*?<small>\((.+?)\)</small>", str_response)

    return q_list


def get_ru_labels(ids, q):
    # https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q42|Q1&props=labels&languages=ru
    url_ru_labels = 'https://www.wikidata.org/w/api.php?format=json&action=wbgetentities&ids=' + ids + '&props=labels&languages=ru'
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

    return existing_title, ru_labels


# labels = ['Зоммер, Янн', 'Тьерсен, Ян', 'Нотра, Ян', 'Ян ЛеКун', 'Янн М’Вила', 'Ян Бон Артюс-Бертран', 'Кеффелек, Ян', 'Бёрон, Ян', 'Капе, Ян', 'Мартел, Янн', 'Ле Гак, Ян']
# print(get_ru_name(labels))
def get_ru_name(labels):
    if len(labels) <= 2:
        return ''

    candidates = defaultdict(int)

    for label in labels:
        label = re.sub('(.*), ', '', label)
        label = label.split(' ')[0]
        candidates[label] += 1

    sorted_cans = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    try:
        print(sorted_cans)
    except:
        ''

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
                    res += ' / ' + k3

    return res


def get_password():
    print("Enter wikidata password: ", end='')
    passwd = input()
    return passwd


def wikidata_login():
    user = 'Botik'
    passw = get_password()
    params = '?action=login&lgname=%s&lgpassword=%s&format=json' % (user, passw)

    # Login request
    r1 = requests.post(baseurl + 'api.php' + params)
    login_token = r1.json()['login']['token']

    # login confirm
    params2 = params + '&lgtoken=%s' % login_token
    r2 = requests.post(baseurl + 'api.php' + params2, cookies=r1.cookies)

    # get edit token
    r3 = requests.get(baseurl + 'api.php' + '?format=json&action=query&meta=tokens&continue=', cookies=r2.cookies)
    edit_token = r3.json()['query']['tokens']['csrftoken']

    edit_cookie = r2.cookies.copy()
    edit_cookie.update(r3.cookies)

    return edit_cookie, edit_token


def wikidata_edit(q, label, description, aliases):
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    if len(label) > 0:
        payload_l = {'format': 'json', 'action': 'wbsetlabel', 'id': q,
                     'summary': 'name from Russian Wikipedia link statistics', 'language': 'ru', 'value': label,
                     'token': edit_token, 'bot': 1}
        r5 = requests.post(baseurl + 'api.php', data=payload_l, headers=headers, cookies=edit_cookie)

    if len(description) > 0:
        payload_d = {'format': 'json', 'action': 'wbsetdescription', 'id': q,
                     'language': 'ru', 'value': description,
                     'token': edit_token, 'bot': 1}
        r4 = requests.post(baseurl + 'api.php', data=payload_d, headers=headers, cookies=edit_cookie)

    if len(aliases) > 0:
        payload_a = {'format': 'json', 'action': 'wbsetaliases', 'id': q,
                     'language': 'ru', 'add': aliases,
                     'token': edit_token, 'bot': 1}
        r6 = requests.post(baseurl + 'api.php', data=payload_a, headers=headers, cookies=edit_cookie)

    return


###############################################################


qlist = [('Q13479698', 'Diogo'), ('Q1986777', 'Nicolaus')]

qlist = get_q_list()

edit_cookie, edit_token = wikidata_login()

for qel in qlist:
    print('--------')

    latin_title = qel[1]
    q = qel[0]

    print(q, latin_title.encode('cp1251', 'replace'))

    if " " in latin_title:
        continue

    # url = "http://www.wikidata.org/w/api.php?format=json&action=wbgetentities&ids="+q+"&props=labels&languages=ru|en"
    # http://wdq.wmflabs.org/api?q=claim[735:7451984]%20AND%20link[ruwiki]
    url_what_have_this_name = 'http://wdq.wmflabs.org/api?q=claim[735:' + q.replace('Q', '') + ']%20AND%20link[ruwiki]'

    response = urllib.request.urlopen(url_what_have_this_name)
    str_response = response.readall().decode('utf-8')
    item_json = json.loads(str_response)

    ids = q
    for i in item_json["items"]:
        ids += '|Q' + str(i)

    print(ids)

    existing_title, ru_labels = get_ru_labels(ids, q)

    print(existing_title.encode('cp1251', 'replace'))
    try:
        print(ru_labels)
    except:
        ''

    new_ru_label = get_ru_name(ru_labels)
    print(new_ru_label)

    if ' / ' in new_ru_label:
        aliases = new_ru_label.replace(' / ', '|')
    else:
        aliases = ''

    descr = 'личное имя - ' + latin_title

    if len(new_ru_label)>0:
        wikidata_edit(q, new_ru_label, descr, aliases)
