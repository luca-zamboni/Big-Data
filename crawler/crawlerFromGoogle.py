# -*- coding: utf-8 -*-

import urllib.request
import xml.etree.ElementTree as ET
import xml
import hashlib
import re
import time
import os.path	# files management and checks
import jsonizer
import parserino

tempnews = []
tags = {}

GOOGLE_NEWS_PATH = "newsG.txt"
PARSE_TAGS_PATH = "crawler/parser.par"
JSON_OUTPUT_PATH = "crawler/output.txt"

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr,' ', raw_html)
  return cleantext

def addToFile(testata, title, date, testo):
	print("Added news from " + testata)
	with open(GOOGLE_NEWS_PATH, "a+") as myfile:
		myfile.write(testata + "\n")
		myfile.write(title + "\n")
		myfile.write(date + "\n")
		myfile.write(testo + "\n")

def load_parse_tags():

	global tags

	f = open(PARSE_TAGS_PATH, "r")
	line = f.readline()
	while True:

		line = f.readline().strip("\n")
		if line == "":
			break

		line = line.split('\t')
		if len(line) == 5:
			testata, attrtype_body, attrtype_body_val, attrtype_title, attrtype_title_val  = line
			tags[testata] = {
				"attrtype_body": attrtype_body,
				"attrtype_body_val": attrtype_body_val,
				"attrtype_title": attrtype_title,
				"attrtype_title_val": attrtype_title_val
			}
		if len(line) == 3:
			testata, attrtype_body, attrtype_body_val = line
			tags[testata] = {
				"attrtype_body": attrtype_body,
				"attrtype_body_val": attrtype_body_val,
				"attrtype_title": "qualcosadiimpossibile",
				"attrtype_title_val": "qualcosadiimpossibile"
			}

	f.close()
			
	

# def took_only_body_from_html(html_text, t):

# 	try:

# 		f = open(PARSE_TAGS_PATH, "r")
# 		line = f.readline()
# 		while True:

# 			line = f.readline().strip("\n")
# 			if line == "":
# 				break
# 			line = line.split('\t')
# 			if len(line) == 5:
# 				testata, attrtype_body, attrtype_body_val, attrtype_title, attrtype_title_val  = line
# 				if(t == testata):
# 					print("beccato", t)
# 					break

# 	except Exception as e:
# 		print("Except:",e)

def insert(news, feed_url):

	nid = 0
	for n in news:

		nid += 1
		title = n.find('title').text
		date = n.find('pubDate').text
		body = n.find('description').text
		news = jsonizer.News(nid = nid, title = title, date = date, body = body, feed_url = feed_url)
		parser = parserino.ParserNews(news)

		source_testata = urllib.request.urlopen(news.get_testata_url()).read()
		try:
			source_testata = source_testata.decode('utf-8')
		except Exception as e:
			source_testata = source_testata.decode('latin1')

		if news.get_testata() in tags:

			parser_source_html = parserino.ParserSource(source_testata, tags[news.get_testata()])
			parsed_title, parsed_body = parser_source_html.parse()

			if parsed_title != "":

				title = parsed_title
				
			if parsed_body != "":

				body = parsed_body

			#print(news.get_testata())

			#if news.get_testata() == "Adnkronos":
				#print(body)


			# Clean title and body
			title = re.sub(' - .*', ' ', title)
			title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
			title = title.rstrip('\t').rstrip('\n')
			news.set_title(title)

			body = re.sub(' - .*', ' ', body)
			body = re.sub('\s+', ' ', body).strip().replace(' ...',' ')
			body = body.rstrip('\t').rstrip('\n')
			news.set_body(body)

			newsFile = open(JSON_OUTPUT_PATH, "r+")
			newsFile.seek(0, os.SEEK_END)
			pos = newsFile.tell() - 1
			while pos > 0 and newsFile.read(1) != "\n":
			    pos -= 1
			    newsFile.seek(pos, os.SEEK_SET)

			if pos > 0:
			    newsFile.seek(pos, os.SEEK_SET)
			    newsFile.truncate()

			newsFile.write('\n},')
			count = len([news])
			for news in [news]:
				newsFile.write(str(news.to_JSON()))
				count -= 1
				if(count > 0):
					newsFile.write(',')
			newsFile.write(']')
			newsFile.close()

			print(news.get_testata())

			# if parsed_body != "":

			# 	print("Ottenuto body buono da testata")

			# 	body = str(parsed_body)

				# # Clean title and body
				# title = re.sub(' - .*', ' ', title)
				# title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
				# title = title.rstrip('\t').rstrip('\n')
				# body = body.rstrip('\t').rstrip('\n')


				# news.set_title(title)
				# news.set_body(body)

				# f = open(JSON_OUTPUT_PATH, 'a')
				# f.write(news.get_testata() + str(news.get_body()))
				# f.close()

		# else:

		# 	str(self.source_html)


			# # Clean title and body
			# title = re.sub(' - .*', ' ', title)
			# title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
			# title = title.rstrip('\t').rstrip('\n')
			# body = body.rstrip('\t').rstrip('\n')


			# news.set_title(title)
			# news.set_body(body)

			# output = "bombo.txt"
			# f = open(output, 'a')

			# # if str(news.to_JSON()) != "":
			# 	# print("vuotiooooo")
			# 	# print(str(news.to_JSON()))


			# # bla = news.get_body().unicode()
			# # bla = unicodedata.normalize('NFKD', bla).encode('ascii','ignore')
			# # print(type(bla))
			# f.write(news.get_body())
			# f.close()


		# break


		# if testo is not None and remove_tags(testo).strip().rstrip('\n') != "":

		# 	testo = testo.strip().rstrip('\n')

		# 	# Parses url testata
		# 	p = re.compile("url=([\w\:\/.-]*)")
		# 	match = p.findall(testo)
		# 	if match != []:
		# 		print("Downloading ", match[0])
		# 		response = urllib.request.urlopen(match[0])
		# 		data = response.read()
		# 		text = data.decode('utf-8')
			
		# 		took_only_body_from_html(text, testata)

		# 	if not os.path.exists(GOOGLE_NEWS_PATH):
		# 		addToFile(RSS, title, date, testo)
				
		# 	else:

		# 		newsFile = open(GOOGLE_NEWS_PATH, "r")
		# 		tempnews = []
				
		# 		while True:
		# 			testataF = newsFile.readline().rstrip('\n')
		# 			titleF = newsFile.readline().rstrip('\n')
		# 			dateF = newsFile.readline().rstrip('\n')
		# 			testoF = newsFile.readline().rstrip('\n')
		# 			if not testataF or not titleF or not dateF or not testoF: break
		# 			tempnews += [(titleF,testataF, dateF)]

		# 		newsFile.close();

		# 		found = False
		# 		for n,t,d in tempnews:
		# 			if n == title:
		# 				found = True
		# 				break;

		# 		if not found:
		# 			addToFile(RSS, title, date, testo)

while(True):
	# try:

	feed = []
	load_parse_tags()

	response = urllib.request.urlopen("https://news.google.it")
	data = response.read()
	text = data.decode('utf-8')

	aTags = re.findall('<a [^>.]*>Copertura live</a>', text)

	xmls = []
	for a in aTags:

		links = re.findall('href="[^".]*"', a)
		url = "https://news.google.it/" + links[0][7:-1]
		response = urllib.request.urlopen(url)
		data = response.read()
		text = data.decode('utf-8')

		hrefRSS = re.findall('<a .*>.*RSS<\/a>', text)
		tmp = re.findall('href="([^"]*)"', hrefRSS[0])[0].replace("amp;", "");
		RSS = "https://" + tmp[7:]
		
		response = urllib.request.urlopen(RSS)
		data = response.read()
		text = data.decode('utf-8')

		root = ET.fromstring(text)
		insert(root.iter('item'), RSS)
		# time.sleep(10)

	# except Exception as e:
	# 	print("Except:",e)
	time.sleep( 120 )