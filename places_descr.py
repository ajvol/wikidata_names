#!/usr/bin/python
# -*- coding: utf-8 -*-


import string
import time
import sys

import urllib.request
import urllib.response
import urllib.parse
import json
import codecs

import urllib
import re

__author__ = 'Alexander Sigachov'

#from pymorphy import get_morph
#morph = get_morph('/home/ajvol/progs/dict')
#print morph.inflect_ru(u"СУСЛИК", u"ед,тв") # много кого?

#http://export.yandex.ru/inflect.xml?name=%D0%94%D1%8D%D0%BD+%D0%A1%D1%8F%D0%BE%D0%BF%D0%B8%D0%BD


#req = urllib2.Request('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&ids=Q45605&props=labels|claims&languages=ru|en&format=json', None, {'user-agent':'syncstream/vimeo'})

#req = urllib2.Request('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&ids=Q45605&props=labels|claims&languages=ru|en&format=json')

#f = opener.open(req)
#data=simplejson.load(f)
#print "Q"+str(data["entities"]["Q45605"]["claims"]["P131"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])

#next_adm_item = data["entities"]["Q45605"]["claims"]["P131"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"]
#current_title = data["entities"]["Q45605"]["labels"]["ru"]["value"]

#id_list=['45605','1058036'] # ржевский район, деревня Михайловка в России
#id_list=['4297458','4297459','4297460','4297462','4297463','4297465','4297466','4297468'] #Украина




countries={}
file = codecs.open("countries2.txt", 'r', encoding='utf-8')
for row in file:
    match = re.search('(.*)\,(.*)', row)
    countries[match.group(1)] = match.group(2)




response = urllib.request.urlopen("http://tools.wmflabs.org/wikidata-terminator/?list&lang=ru")
start_data0 = response.readall().decode('utf-8')


items_without_descriptions = re.findall( "term\=(.+?)\&doit", start_data0, re.IGNORECASE )

j=0

for myid0 in items_without_descriptions:

    j=j+1
    if j>20:
        break

    try:
        print ('===== NEW TERM ======')
        print (myid0)
        print (urllib.parse.unquote(myid0))

        response = urllib.request.urlopen("http://tools.wmflabs.org/wikidata-terminator/?lang=ru&term="+myid0+"&doit=1")
        start_data = response.readall().decode('utf-8')

        start_data = start_data.replace('<tr>','\n<tr>')

        #id_list = re.findall( "wiki/Q(\d+)'", start_data, re.IGNORECASE )
        id_list = re.findall( "wiki/Q(\d+)'>.*\/td.*\/td.*><\/td><\/tr>", start_data, re.IGNORECASE )
    except:
        continue



    for myid in id_list:
        try:
            #myid='56151'
            print("   "+myid)

            adm_type_id=''
            if myid[0:1]=='Q':
                next_adm_item=myid
            else:
                next_adm_item='Q'+myid
            adm_sequence=[]
            description=''
            ru_wiki_page=''
            wiki_text=''

            for i in range(1, 6):
                # http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=labels|claims|sitelinks&languages=ru|en&format=json&ids=Q18779470
                response = urllib.request.urlopen('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=labels|claims|sitelinks&languages=ru|en&format=json&ids='+next_adm_item)
                str_response = response.readall().decode('utf-8')
                data=json.loads(str_response)

                # P31 - частный случай понятия
                if i==1 and "claims" in data["entities"][next_adm_item] and "P31" in data["entities"][next_adm_item]["claims"]:
                    adm_type_id = "Q"+str(data["entities"][next_adm_item]["claims"]["P31"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])

                if i==1 and "ruwiki" in data["entities"][next_adm_item]["sitelinks"]:
                    ru_wiki_page = data["entities"][next_adm_item]["sitelinks"]["ruwiki"]["title"]

                try:
                    current_title = data["entities"][next_adm_item]["labels"]["ru"]["value"]
                    current_title = re.sub('\(.*\)', '', current_title)
                except:
                    current_title = ''

                if current_title != '':
                    adm_sequence.append(current_title)

                # P131 - административно-территориальная единица
                if "claims" in data["entities"][next_adm_item] and "P131" in data["entities"][next_adm_item]["claims"]:
                    next_adm_item = "Q"+str(data["entities"][next_adm_item]["claims"]["P131"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])
                else:
                    break


            seen_list=set()
            for itm in (adm_sequence[::-1])[:-1]:
                itm = re.sub('\(.*\)', '', itm)
                itm = re.sub('\<.*\>', '', itm)
                itm = re.sub('\[\[', '', itm)
                itm = re.sub('\]\]', '', itm)
                itm = re.sub('\{\{\!\}\}.*', '', itm)

                itm = itm.replace('сельский совет','сельсовет')

                itm=itm.strip()

                if itm in countries:
                    itm=countries[itm]


                if (itm != '') and (itm not in seen_list):
                    seen_list.add(itm)
                    description=description + itm + ', '



            if adm_type_id != '':
                response = urllib.request.urlopen('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=labels&languages=ru&format=json&ids='+adm_type_id)
                str_response = response.readall().decode('utf-8')
                data=json.loads(str_response)

                adm_type=data["entities"][adm_type_id]["labels"]["ru"]["value"]

                adm_type = adm_type.replace(' в России','')
                adm_type = adm_type.lower()


            else:
                if ru_wiki_page != '':
                    escaped = urllib.parse.quote(ru_wiki_page.encode('utf-8'))

                    response = urllib.request.urlopen('http://ru.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles='+escaped)
                    str_response = response.readall().decode('utf-8')
                    data=json.loads(str_response)

                    for itm in data["query"]["pages"]:
                        wiki_text=wiki_text=data["query"]["pages"][itm]["revisions"][0]["*"]

                    match0 = re.search( '.*\{\{.*НП.*', wiki_text )
                    match = re.search( '.*(статус|Тип)\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is None or match0 is None:
                        adm_type = ''
                    else:
                        adm_type = match.group(2).strip().lower()
                        adm_type = adm_type.replace('{{s|','')
                        adm_type = adm_type.replace('}}','')
                        adm_type = adm_type.replace(']]','')
                        adm_type = adm_type.replace('[[','')
                        #adm_type = adm_type.replace('муниципальный','')
                        adm_type = adm_type.strip()

                    if adm_type == '':
                        match = re.search( '.*НП-.*\|.*\|(.*)', wiki_text, re.IGNORECASE )
                        if match is None:
                            adm_type = ''
                        else:
                            adm_type = match.group(1).strip().lower()
                            adm_type = adm_type.replace('{{s|','')
                            adm_type = adm_type.replace('}}','')
                            adm_type = adm_type.replace('[[','')
                            adm_type = adm_type.replace(']]','')
                            #adm_type = adm_type.replace('муниципальный','')
                            adm_type = adm_type.strip()



            if description.strip() == '' and ru_wiki_page != '':
                adm_sequence=[]

                if wiki_text == '':
                    escaped = urllib.parse.quote(ru_wiki_page.encode('utf-8'))

                    response = urllib.request.urlopen('http://ru.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles='+escaped)
                    str_response = response.readall().decode('utf-8')
                    data=json.loads(str_response)

                    for itm in data["query"]["pages"]:
                        wiki_text=wiki_text=data["query"]["pages"][itm]["revisions"][0]["*"]





                match = re.search( '.*НП-Украина.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(re.sub('\<.*\>', '', match.group(1).strip()))

                    match = re.search( '.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        tmp = match.group(1).strip()
                        tmp = re.sub('район.*', 'район', tmp)
                        adm_sequence.append(tmp.strip())

                    match = re.search( '.*\|область\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Украина'.strip())


                match = re.search( '.*НП-Белоруссия.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(re.sub('\<.*\>', '', match.group(1).strip()))

                    match = re.search( '.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        tmp = match.group(1).strip()
                        tmp = re.sub('район.*', 'район', tmp)
                        adm_sequence.append(tmp.strip())

                    match = re.search( '.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Белоруссия'.strip())

                match = re.search( '.*Населённый пункт Украины.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|Подчинён совету\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        tmp = match.group(1).strip()
                        tmp = re.sub('район.*', 'район', tmp)
                        adm_sequence.append(tmp.strip())

                    match = re.search( '.*\|Область\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Украина'.strip())


                match = re.search( '.*НП.Россия.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|поселение\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Россия'.strip())


                match = re.search( '.*НП-Молдавия.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|коммуна\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Молдавия'.strip())

                match = re.search( '.*НП-Казахстан.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    adm_sequence.append('self')

                    match = re.search( '.*\|поселение\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    adm_sequence.append('Казахстан'.strip())

                match = re.search( '\{\{Река.*', wiki_text, re.IGNORECASE )
                if match is not None:
                    description=''

                    match = re.search( '.*\((.*)\).*', ru_wiki_page, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='' and match.group(1).strip()!='река':
                        description = ', ' + match.group(1).strip()

                    match = re.search( '.*\|Регион\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        description = description + ', ' + match.group(1).strip()

                match = re.search( '.*\{\{НП.*', wiki_text, re.IGNORECASE )
                if match is not None and len(adm_sequence)==0:
                    adm_sequence.append('self')

                    match = re.search( '.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(re.sub('\<.*\>', '', match.group(1).strip()))

                    match = re.search( '.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())

                    match = re.search( '.*\|страна\s*\=(.*)', wiki_text, re.IGNORECASE )
                    if match is not None and match.group(1).strip()!='':
                        adm_sequence.append(match.group(1).strip())


                seen_list=set()
                for itm in (adm_sequence[::-1])[:-1]:
                    itm = re.sub('\(.*\)', '', itm)
                    itm = re.sub('\<.*\>', '', itm)
                    itm = re.sub('\[\[', '', itm)
                    itm = re.sub('\]\]', '', itm)
                    itm = re.sub('\{\{\!\}\}.*', '', itm)

                    itm=itm.replace('Автономная Республика Крым','Крым')
                    itm=itm.replace('сельский совет','сельсовет')

                    itm=itm.strip()

                    if itm in countries:
                        itm=countries[itm]


                    if (itm != '') and (itm not in seen_list):
                        seen_list.add(itm)
                        description=description + itm + ', '


            match = re.search( '(.*)(община|муниципалитет|коммунна|коммуна|департамент|округ|провинция|графство|кантон|область|административный регион|посёлок|село|город|тауншип|специальный район|деревня|уезд|волость)(.*)', adm_type, re.IGNORECASE )
            if match is not None:
                adm_type=match.group(2).strip()

            description = description.replace('река, река','река')



            if adm_type.strip() == 'страница значений в проекте викимедиа':
                final_description =  'страница значений'

            elif adm_type.strip() == 'река' and description[0]==',':
                final_description =  adm_type + description.strip()

            elif description.strip() != '' and adm_type.strip() != '':
                if description[0:2]=='в ' or description[0:3]=='на ' or description[0:3]=='во ':
                    description = description[:-2]
                    final_description = adm_type+' '+description
                else:
                    description = description[:-2]
                    final_description = adm_type+' - '+description
            else:
                print ('Empty description. Adm_type='+adm_type)
                final_description = ''


            print ("   "+str(myid) + ': ' +final_description)


            #item = pywikibot.ItemPage(repo, 'Q'+str(myid) )

            if 1==0: #'ru' in item.descriptions:
                print ('The label in Russian is: ' + item.descriptions['ru'])
            elif final_description != '':
                print("")
            else:
                print ('Empty description!')

        except Exception as e:
            print ('Unknown error:')
            print (e)
            time.sleep(5)






# cd ~/progs/pywikibot/core
#ajvol@ubuntu:~/progs/pywikibot/core$ python pwb.py myscripts/test_wd.py


# subjekt RF vishe etogo objekta
#claim[132:835714,132:831740,132:309166,132:184122,132:183342,132:41162] AND tree[45605][131]

# vse visestoyasch sub
#http://208.80.153.172/api?q=tree[1060604][131]&labels=ru&props=P132

#определяем по одному вышестоящие адм единицы


"""
site = pywikibot.Site('wikidata')
repo = site.data_repository() 

item = pywikibot.ItemPage(repo, 'Q45605')  

item.get() #  you need to call it to access any data.

if 'ru' in item.descriptions:
    print 'The label in Russian is: ' + item.descriptions['ru']
else:
    print 'No description'
"""

'''
print "id"
print item.id
print "\nsitelinks:"
print item.sitelinks
print "\naliases:"
print item.aliases
print "\nlabels:"
print item.labels
print "\ndescriptions:"
print item.descriptions
'''
