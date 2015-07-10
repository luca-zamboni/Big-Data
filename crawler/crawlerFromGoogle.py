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
from socket import timeout

tempnews = []
tags = {}
sentences_to_ignore = []
nid = 0

GOOGLE_NEWS_PATH = "newsG.txt"
PARSE_TAGS_PATH = "crawler/parser.par"
SENTENCES_TO_IGNORE_PATH = "crawler/sentences_to_ignore.txt"
JSON_OUTPUT_PATH = "crawler/output_test.json"

def load_sentences_to_ignore():

	global sentences_to_ignore

	if sentences_to_ignore != []:
		return;

	f = open(SENTENCES_TO_IGNORE_PATH, "r")
	while True:

		line = f.readline().strip("\n")
		if line == "":
			break

		line = line.split('\t')

		sentences_to_ignore += [line[1]]

	f.close()

def load_parse_tags():

	global tags

	if tags != {}:
		return;

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
				"attrtype_title": "",
				"attrtype_title_val": ""
			}

	f.close()

def clean_string(string):
	# string = re.sub(' - .*', ' ', string)
	string = re.sub('[\\\""]', '', string)
	string = re.sub('\'', ' ', string)
	# string.rstrip('- ').rstrip(' -')
	string = re.sub('\s+', ' ', string).replace(' ...',' ')
	string = string.rstrip('\t').rstrip('\n')
	return string

def remove_sentences_to_ignore(body):
	for s in sentences_to_ignore:
		body = re.sub(s+'.*', ' ', body)
	return body

load_parse_tags()

def store_news_in_file(news):

	global nid

	try:

		if os.path.exists(JSON_OUTPUT_PATH):

			# Open in read and truncate the last row which contains ]}
			# and add a new one with }, so a new {news.to_JSON} can be added.
			newsFile = open(JSON_OUTPUT_PATH, 'r+')
			newsFile.seek(0, os.SEEK_END)
			pos = newsFile.tell() - 1
			while pos > 0 and newsFile.read(1) != "\n":
			    pos -= 1
			    newsFile.seek(pos, os.SEEK_SET)

			if pos > 0:
			    newsFile.seek(pos, os.SEEK_SET)
			    newsFile.truncate()

			newsFile.write('\n},')

		else:

			newsFile = open(JSON_OUTPUT_PATH, 'w')

		# No matter what, write the news..
		newsFile.write(news.to_JSON())
		newsFile.write(']')
		newsFile.close()
		nid += 1
		return True

	except Exception as e:
		print(e)
		return False

def dowload_testata_from_source(url):

	# url = "http://www.corrieredellosport.it/news/calcio/calcio-mercato/2015/07/08-2262837/cr7_al_psg_libera_ibra_al_milan"

	try:
		print("Downloading: ", url)
		source_testata = urllib.request.urlopen(url, timeout = 10).read()
	except Exception as e:
		print("Exception in dowload_testata_from_source():", e)
		return ""

	try:
		print("Try to decode in utf-8")
		return source_testata.decode('utf-8')
	except Exception as e:
		pass

	try:
		print("Try to decode in latin-1")
		return source_testata.decode('latin1')
	except Exception as e:
		pass

	print("Can't decode!")
	return ""

def get_testata_source_and_write_on_file(news):

	print(news.get_testata())

	if news.get_testata() in tags:

		source = dowload_testata_from_source(news.get_testata_url())

		# Check if the download is successful
		if source != "":

			print("Download source testata riuscito.")

			body = news.get_body()
			title = news.get_title()	

			try:
				# news.set_testata("Corriere dello Sport.it")
				parser_source_html = parserino.ParserSource(source, tags[news.get_testata()])
				parsed_title, parsed_body = parser_source_html.parse()
			except Exception as e:
				print("Exception in get_testata_source_and_write_on_file():", e)
				parsed_title, parsed_body = "", ""
				pass

			if parsed_title != "":
				print("Ho aggiornato il titolo")
				title = parsed_title
				
			if parsed_body != "":
				print("Ho aggiornato il body")
				body = parsed_body

			# Clean title and body from porcherie..
			title = clean_string(title)
			title = remove_sentences_to_ignore(str(title))
			news.set_title(title)
			body = str(body)
			body = clean_string(body)
			body = remove_sentences_to_ignore(str(body))
			news.set_body(body)
	
	else:

		print("Non posso scaricare")
	
	return store_news_in_file(news)

def parse_news_from_google(news):

	parser = parserino.ParserNews(news)
		
	# Testata url is successfully parsed
	if parser.parse():

		# DEBUG
		# if news.get_testata() != "La Stampa":
		# 	return False


		print(news.get_testata_url())
		print("News ha un titolo e body corto, provo a scaricare..")

		# Try to get and store the body of the news given testata_url
		try:

			if get_testata_source_and_write_on_file(news):

				print("Hey, successfully parsed, and store! :)")
				return True
			else:

				return False
		
		except Exception as e:
			print("Exception in parse_list_news_from_google():", e)
			print("Unable to parse or store the following news:", title)
			pass

	return False

def parse_list_news_from_google(news, feed_url):

	for n in news:
		
		title = n.find('title').text
		date = n.find('pubDate').text
		body = n.find('description').text
		news = jsonizer.News(nid = nid, title = title, date = date, body = body, feed_url = feed_url)

		parse_news_from_google(news)

def main():


	load_parse_tags()
	load_sentences_to_ignore()

	while(True):

		try:

			feed = []
			xmls = []

			response = urllib.request.urlopen("https://news.google.it")
			data = response.read()
			text = data.decode('utf-8')
			aTags = re.findall('<a [^>.]*>Copertura live</a>', text)
			
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
				parse_list_news_from_google(root.iter('item'), RSS)
				time.sleep(1)

		except Exception as e:
			print("Except:",e)
		# time.sleep( 120 )


if __name__ == "__main__":
	main()