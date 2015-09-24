#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.response
from collections import defaultdict
import json
import re
import requests

__author__ = 'Ajvol'

def get_text_by_url(url):
    response = urllib.request.urlopen(url)
    return response.readall().decode('utf-8')

def get_json_by_url(url):
    txt =  get_text_by_url(url)
    return json.loads(txt)

def get_ru_label_by_ce_label(ce_label):
    escp = urllib.parse.quote(ce_label.capitalize().encode('utf-8'))
    d = get_json_by_url('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=cewiki&props=labels&languages=ru&format=json&titles=' + escp)
    print(d)
    if "entities" in d:
        for q in d["entities"]:
            if "labels" in d["entities"][q] and "ru" in d["entities"][q]["labels"]:
                return d["entities"][q]["labels"]["ru"]["value"]
            break

print (get_ru_label_by_ce_label('эвла'))