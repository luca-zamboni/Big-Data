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
import string
from socket import timeout
from polyglot.text import Text

tempnews = []
tags = {}
sentences_to_ignore = []
nid = 0

GOOGLE_NEWS_PATH = "newsG.txt"
PARSE_TAGS_PATH = "crawler/parser.par"
SENTENCES_TO_IGNORE_PATH = "crawler/sentences_to_ignore.txt"
JSON_OUTPUT_PATH = "crawler/output_test.json"

MIN_NUM_KEYWORDS = 4

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
	string = re.sub('[\\\""\|]', '', string)
	string = re.sub('\\\"', '', string)
	# string = re.sub('\'', ' ', string)
	# string = re.sub('\s+', ' ', string)
	string = string.replace(' ...','')
	string = string.replace('\t','')
	string = string.replace('\n','')
	string = ' '.join(string.split())
	return string

def remove_sentences_to_ignore(body):
	for s in sentences_to_ignore:
		body = re.sub(s+'.*', ' ', body)
	return body

def get_keyword_from_string(text):
	text = Text(text)
	keywords = []
	for entity in text.entities:
		for e in entity:
			keywords = keywords + [str(e)]

	#  Are enough keywords to deal with?
	if len(keywords) < MIN_NUM_KEYWORDS:
		return ""

	# Removes duplicate keywords
	no_duplicates = set(keywords)
	keywords = list(no_duplicates)
	keywords = " ".join(keywords).lower()

	for c in string.punctuation:
		keywords = keywords.replace(c, '')

	return ' '.join(keywords.split())

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
			newsFile.write('[')

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

	# url = "http://economia.ilmessaggero.it/economia_e_finanza/grecia-tsipras-default-fmi/1438685.shtml"

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

	body = news.get_body()
	title = news.get_title()

	if news.get_testata() in tags:

		source = dowload_testata_from_source(news.get_testata_url())

		# Check if the download is successful
		if source != "":

			try:
				# news.set_testata("Il Messaggero")
				parser_source_html = parserino.ParserSource(source, tags[news.get_testata()])
				parsed_title, parsed_body = parser_source_html.parse()
			except Exception as e:
				print("Exception in get_testata_source_and_write_on_file():", e)
				parsed_title, parsed_body = "", ""
				pass

			if parsed_title != "":
				title = parsed_title
				
			if parsed_body != "":
				body = parsed_body

	# Clean title and body from porcherie..
	# Indentation in REALLY IMPORTANT HERE!
	try:

		title = clean_string(str(title))
		title = remove_sentences_to_ignore(str(title))
		title = title.replace(news.get_testata(),'')
		news.set_title(title)

		body = clean_string(str(body))
		body = remove_sentences_to_ignore(str(body))
		news.set_body(body)

		keywords = get_keyword_from_string(title + body)
		news.set_keywords(keywords)

	except Exception as e:

		print("Exception in get_testata_source_and_write_on_file():", e)
		return False
	
	return store_news_in_file(news)

def parse_news_from_google(news):

	parser = parserino.ParserNews(news)
		
	# Testata url is successfully parsed
	if parser.parse():

		print("I am trying to donwload from", news.get_testata_url())

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
				time.sleep(4) # sleep 2

		except Exception as e:
			print("Except:",e)
		# time.sleep( 120 )


if __name__ == "__main__":
	main()