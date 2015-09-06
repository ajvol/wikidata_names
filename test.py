#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from collections import defaultdict

__author__ = 'Ajvol'


def get_ru_names(labels):
    if len(labels) <= 2:
        return 'null'

    candidates = defaultdict(int)

    for label in labels:
        label =  re.sub('(.*), ', '', label)
        label = label.split(' ')[0]
        candidates[label] += 1

    print(candidates)

    res = ''
    uniques_num = len(candidates.keys())
    sorted_cans = sorted(candidates.items(), key=lambda x: x[1], reverse=True)
    print(sorted_cans)

    k,v = sorted_cans[0]
    print(k)



    return res


labels = ['Ке де Сент-Эмур, Амедей', 'Амедей Боррель', 'Курбе, Амедей Анатоль Проспер', 'Жибо, Амедей', 'Роллан, Амедей', 'Тьерри, Амедей', 'Лами, Франсуа-Жозеф-Амеде', 'Пишо, Амедей', 'Лепелетье, Амедей Луи Мишель', 'Муше, Эрнест Амедей Бартелеми', 'Баст, Амеде де', 'Озанфан, Амеде', 'Меро, Амедей', 'Лагарп, Амедей Эммануэл']
print(get_ru_names(labels))