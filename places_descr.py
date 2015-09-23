#!/usr/bin/python
# -*- coding: utf-8 -*-

import pwb #only needed if you haven't installed the framework as side-package
import pywikibot
import string
import time
import sys

import urllib2
import simplejson
import codecs

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



import urllib
import re

countries={}
file = codecs.open("myscripts/countries2.txt", 'r', encoding='utf-8')
for row in file:
	match = re.search( ur'(.*)\,(.*)', row)
	countries[match.group(1)] = match.group(2)


#site = pywikibot.Site('wikidata')
site = pywikibot.Site('en','wikipedia')
repo = site.data_repository() 







list_opener = urllib2.build_opener()

req0 = urllib2.Request("http://tools.wmflabs.org/wikidata-terminator/?list&lang=ru")
in_0 = list_opener.open(req0)
start_data0 = in_0.read()


id_list0 = re.findall( ur"term\=(.+?)\&doit", start_data0, re.IGNORECASE )

j=0

for myid0 in id_list0:

	j=j+1
	if j<700:
		continue

	try:
		print '===== NEW TERM ======'
		print urllib2.unquote(myid0)

		first_opener = urllib2.build_opener()

		req = urllib2.Request("http://tools.wmflabs.org/wikidata-terminator/?lang=ru&term="+myid0+"&doit=1")
		in_ = first_opener.open(req)
		start_data = in_.read()
		#print start_data

		start_data = start_data.replace('<tr>','\n<tr>')

		#id_list = re.findall( ur"wiki/Q(\d+)'", start_data, re.IGNORECASE )
		id_list = re.findall( ur"wiki/Q(\d+)'>.*\/td.*\/td.*><\/td><\/tr>", start_data, re.IGNORECASE )
	except:
		continue



	for myid in id_list:
		try:
			#myid='56151'

			adm_type_id=u''
			if myid[0:1]==u'Q':
				next_adm_item=myid
			else:
				next_adm_item=u'Q'+myid
			adm_sequence=[]
			description=u''
			ru_wiki_page=u''
			wiki_text=u''

			opener = urllib2.build_opener()

			for i in range(1, 6):
				req = urllib2.Request('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=labels|claims|sitelinks&languages=ru|en&format=json&ids='+next_adm_item)
				f = opener.open(req)
				data=simplejson.load(f)

				# P132 - тип административной единицы
				if i==1 and "claims" in data["entities"][next_adm_item] and "P132" in data["entities"][next_adm_item]["claims"]:
					adm_type_id = "Q"+str(data["entities"][next_adm_item]["claims"]["P132"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])

				# P31 - частный случай понятия
				if i==1 and "claims" in data["entities"][next_adm_item] and "P31" in data["entities"][next_adm_item]["claims"]:
					adm_type_id = "Q"+str(data["entities"][next_adm_item]["claims"]["P31"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])

				if i==1 and "ruwiki" in data["entities"][next_adm_item]["sitelinks"]:
					ru_wiki_page = data["entities"][next_adm_item]["sitelinks"]["ruwiki"]["title"]

				try:
					current_title = data["entities"][next_adm_item]["labels"]["ru"]["value"]
					current_title = re.sub(ur'\(.*\)', ur'', current_title)
				except:
					current_title = u''

				if current_title != u'':
					adm_sequence.append(current_title)

				if "claims" in data["entities"][next_adm_item] and "P131" in data["entities"][next_adm_item]["claims"]:
					next_adm_item = "Q"+str(data["entities"][next_adm_item]["claims"]["P131"][0]["mainsnak"]["datavalue"]["value"]["numeric-id"])	
				else:
					break


			seen_list=set()
			for itm in (adm_sequence[::-1])[:-1]:
				itm = re.sub(ur'\(.*\)', ur'', itm)
				itm = re.sub(ur'\<.*\>', ur'', itm)
				itm = re.sub(ur'\[\[', ur'', itm)
				itm = re.sub(ur'\]\]', ur'', itm)
				itm = re.sub(ur'\{\{\!\}\}.*', ur'', itm)

				itm = itm.replace(u'сельский совет',u'сельсовет')

				itm=itm.strip()

				if itm in countries:
					itm=countries[itm]
				

				if (itm != u'') and (itm not in seen_list):
					seen_list.add(itm)
					description=description + itm + u', '



			if adm_type_id != u'':
				req = urllib2.Request('http://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&props=labels&languages=ru&format=json&ids='+adm_type_id)
				f = opener.open(req)
				data=simplejson.load(f)
				adm_type=data["entities"][adm_type_id]["labels"]["ru"]["value"]

				adm_type = string.replace(adm_type,u' в России',u'')
				adm_type = string.lower(adm_type)


			else:
				if ru_wiki_page != u'':
					escaped = urllib.quote(ru_wiki_page.encode('utf-8'))

					req = urllib2.Request('http://ru.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles='+escaped)
					f = opener.open(req)
					data=simplejson.load(f)

					for itm in data["query"]["pages"]:
						wiki_text=wiki_text=data["query"]["pages"][itm]["revisions"][0]["*"]

					match0 = re.search( ur'.*\{\{.*НП.*', wiki_text )
					match = re.search( ur'.*(статус|Тип)\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is None or match0 is None:
						adm_type = u''
					else:
						adm_type = match.group(2).strip().lower()
						adm_type = string.replace(adm_type,u'{{s|',u'')
						adm_type = string.replace(adm_type,u'}}',u'')
						adm_type = string.replace(adm_type,u']]',u'')
						adm_type = string.replace(adm_type,u'[[',u'')
						#adm_type = string.replace(adm_type,u'муниципальный',u'')
						adm_type = adm_type.strip()

					if adm_type == u'':
						match = re.search( ur'.*НП-.*\|.*\|(.*)', wiki_text, re.IGNORECASE )
						if match is None:
							adm_type = u''
						else:
							adm_type = match.group(1).strip().lower()
							adm_type = string.replace(adm_type,u'{{s|',u'')
							adm_type = string.replace(adm_type,u'}}',u'')
							adm_type = string.replace(adm_type,u'[[',u'')
							adm_type = string.replace(adm_type,u']]',u'')
							#adm_type = string.replace(adm_type,u'муниципальный',u'')
							adm_type = adm_type.strip()



			if description.strip() == u'' and ru_wiki_page != u'':
				adm_sequence=[]

				if wiki_text == u'':
					escaped = urllib.quote(ru_wiki_page.encode('utf-8'))

					req = urllib2.Request('http://ru.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&rvprop=content&titles='+escaped)
					f = opener.open(req)
					data=simplejson.load(f)

					for itm in data["query"]["pages"]:
						wiki_text=wiki_text=data["query"]["pages"][itm]["revisions"][0]["*"]





				match = re.search( ur'.*НП-Украина.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(re.sub(ur'\<.*\>', ur'', match.group(1).strip()))				

					match = re.search( ur'.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						tmp = match.group(1).strip()
						tmp = re.sub(ur'район.*', ur'район', tmp)
						adm_sequence.append(tmp.strip())

					match = re.search( ur'.*\|область\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Украина'.strip())


				match = re.search( ur'.*НП-Белоруссия.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(re.sub(ur'\<.*\>', ur'', match.group(1).strip()))

					match = re.search( ur'.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						tmp = match.group(1).strip()
						tmp = re.sub(ur'район.*', ur'район', tmp)
						adm_sequence.append(tmp.strip())

					match = re.search( ur'.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Белоруссия'.strip())

				match = re.search( ur'.*Населённый пункт Украины.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|Подчинён совету\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|район в таблице\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						tmp = match.group(1).strip()
						tmp = re.sub(ur'район.*', ur'район', tmp)
						adm_sequence.append(tmp.strip())

					match = re.search( ur'.*\|Область\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Украина'.strip())


				match = re.search( ur'.*НП.Россия.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|поселение\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Россия'.strip())


				match = re.search( ur'.*НП-Молдавия.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|коммуна\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Молдавия'.strip())

				match = re.search( ur'.*НП-Казахстан.*', wiki_text, re.IGNORECASE )
				if match is not None:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|поселение\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					adm_sequence.append(u'Казахстан'.strip())

				match = re.search( ur'\{\{Река.*', wiki_text, re.IGNORECASE )
				if match is not None:
					description=u''

					match = re.search( ur'.*\((.*)\).*', ru_wiki_page, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'' and match.group(1).strip()!=u'река':
						description = u', ' + match.group(1).strip()

					match = re.search( ur'.*\|Регион\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						description = description + u', ' + match.group(1).strip()

				match = re.search( ur'.*\{\{НП.*', wiki_text, re.IGNORECASE )
				if match is not None and len(adm_sequence)==0:
					adm_sequence.append(u'self')

					match = re.search( ur'.*\|община\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(re.sub(ur'\<.*\>', ur'', match.group(1).strip()))

					match = re.search( ur'.*\|район\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|регион\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())

					match = re.search( ur'.*\|страна\s*\=(.*)', wiki_text, re.IGNORECASE )
					if match is not None and match.group(1).strip()!=u'':
						adm_sequence.append(match.group(1).strip())


				seen_list=set()
				for itm in (adm_sequence[::-1])[:-1]:
					itm = re.sub(ur'\(.*\)', ur'', itm)
					itm = re.sub(ur'\<.*\>', ur'', itm)
					itm = re.sub(ur'\[\[', ur'', itm)
					itm = re.sub(ur'\]\]', ur'', itm)
					itm = re.sub(ur'\{\{\!\}\}.*', ur'', itm)

					itm=itm.replace(u'Автономная Республика Крым',u'Крым')
					itm=itm.replace(u'сельский совет',u'сельсовет')

					itm=itm.strip()

					if itm in countries:
						itm=countries[itm]
					

					if (itm != u'') and (itm not in seen_list):
						seen_list.add(itm)
						description=description + itm + u', '


			match = re.search( ur'(.*)(община|муниципалитет|коммунна|коммуна|департамент|округ|провинция|графство|кантон|область|административный регион|посёлок|село|город|тауншип|специальный район|деревня|уезд|волость)(.*)', adm_type, re.IGNORECASE )
			if match is not None:
				adm_type=match.group(2).strip()
		
			description = description.replace(u'река, река',u'река')
			


			if adm_type.strip() == u'страница значений в проекте викимедиа':
				final_description =  u'страница значений'

			elif adm_type.strip() == u'река' and description[0]==',':
				final_description =  adm_type + description.strip()

			elif description.strip() != u'' and adm_type.strip() != u'':
				if description[0:2]==u'в ' or description[0:3]==u'на ' or description[0:3]==u'во ':
					description = description[:-2]
					final_description = adm_type+u' '+description
				else:
					description = description[:-2]
					final_description = adm_type+u' - '+description					
			else:
				print 'Empty description. Adm_type='+adm_type
				final_description = u''


			print str(myid) + u': ' +final_description


			item = pywikibot.ItemPage(repo, 'Q'+str(myid) )  

			item.get() #  you need to call it to access any data.

			if 'ru' in item.descriptions:
				print 'The label in Russian is: ' + item.descriptions['ru']
			elif final_description != u'':
				mydescriptions = {u'ru': final_description}
				try:
					item.editDescriptions(mydescriptions, summary=u'adding Russian description')
				except Exception as err:
					print u'API ERROR'
			else:
				print u'Empty description!'

		except Exception, e:
			print 'Unknown error:'
			print e
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
