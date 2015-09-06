#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.response
from collections import defaultdict
import json
import re
import requests

__author__ = 'Ajvol'


user    = 'Botik'
passw   = ''
baseurl = 'https://www.wikidata.org/w/'
params  = '?action=login&lgname=%s&lgpassword=%s&format=json'% (user,passw)
summary='test'

# Login request
r1 = requests.post(baseurl+'api.php'+params)
login_token = r1.json()['login']['token']

#login confirm
params2 = params+'&lgtoken=%s'% login_token
r2 = requests.post(baseurl+'api.php'+params2, cookies=r1.cookies)

#get edit token
r3 = requests.get(baseurl+'api.php'+'?format=json&action=query&meta=tokens&continue=', cookies=r2.cookies)
edit_token = r3.json()['query']['tokens']['csrftoken']

edit_cookie = r2.cookies.copy()
edit_cookie.update(r3.cookies)

# save action

val = 'Сеппо'

headers = {'content-type': 'application/x-www-form-urlencoded'}
payload = {'format': 'json', 'action': 'wbsetlabel', 'id': 'Q7451984', 'summary': summary, 'language': 'ru', 'value': val, 'token': edit_token}
r4 = requests.post(baseurl+'api.php', data=payload, headers=headers, cookies=edit_cookie)
print (r4.text)