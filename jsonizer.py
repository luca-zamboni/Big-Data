# -*- coding: utf-8 -*-

import json     	# JSON
# import codecs 		# For encoding and decoding of json files
import unicodedata 	# For encoding and decoding of json files
import string 		# Strings
import re 			# Regular Expressions
import os
import os.path 		# Files management and checks
import timeit		# Timer
import time
from HTMLParser import HTMLParser

# Spark
from pyspark import SparkContext

# Global variables
# -----------------------------------------------------------------------------

GOOGLE_NEWS_PATH 	= "newsG.txt"
JSON_NEWS_PATH 	= "newsG.json"
STOP_WORDS_PATH 	= "stopword.txt"
URL_FIRST_PAGE_NEWS = "https://news.google.it/news?pz=1&cf=all&ned=it&hl=it"
CATEGORIES_FOLDER = "crawler/categories/"
categories = [ 'Esteri', 'Italia', 'Economia' , 'Scienza e tecnologia' , 'Intrattenimento' , 'Sport' , 'Salute' ]

stop_words = []			# Contains words: [ 'a', 'b', 'c', ... ]

clusters = {} 								# Dictionary for clusters { string => number }
array_clusters = [[] for i in categories]	# Array of clusters (e.g. [[1],[2,3,4,5,6],[7,8,9,10]])


# -----------------------------------------------------------------------------

class MyHTMLParser(HTMLParser):

	def __init__(self, news):

		HTMLParser.__init__(self)

		self.count_a = 0;
		self.count_font = 0;
		self.current_tag = ""

		self.looking_for_testata = False

		self.news = news
		self.parse_news()

	def parse_news(self):
		self.news.set_source(re.sub("&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));"," ", self.news.get_source()))
		self.feed(self.news.get_source())

	def handle_starttag(self, tag, attrs):

		self.current_tag = tag
		
		if tag == 'a':
			self.count_a += 1
		elif tag == 'font':
			self.count_font += 1
		elif tag == 'td':
			self.count_font = 0

		for tag_name, value in attrs:

			if tag == 'font' and tag_name == 'color' and value == '#6f6f6f':
				self.looking_for_testata = True

			if tag == 'img' and tag_name == "src" and self.count_a == 1:
				self.news.set_image_url(value)

	def handle_data(self, data):

		# TESTATA
		if self.current_tag == "font":
			if self.looking_for_testata:
				self.news.set_testata(data)
				self.looking_for_testata = False
			elif self.count_font == 4:
				txt = self.news.get_description() + data;
				self.news.set_description(removePuntuaction(txt))

class WrapNews:

	def __init__(self, feed_url = "", nid = 0, title = "", testata = "", date = "", body = "", source_url = "", image_url = "", cluster_number = 0):

		self.set_nid(nid)
		self.set_title(title)
		self.set_testata(testata)
		self.set_date(date)
		self.set_body(body)
		self.set_source_url(source_url)
		self.set_image_url(image_url)
		self.set_cluster_number(cluster_number)
		self.set_feed_url(feed_url)

	# URL

	def get_feed_url(self):
		return self.feed_url

	def set_feed_url(self, feed_url):
		self.feed_url = feed_url

	# NEWS - ID

	def get_nid(self):
		return self.nid

	def set_nid(self, nid):
		self.nid = nid

	# TITLE

	def get_title(self):
		return self.title

	def set_title(self, title):
		self.title = title.lower()

	# TESTATA

	def get_testata(self):
		return self.testata

	def set_testata(self, testata):
		self.testata = testata

	# DATE

	def get_date(self):
		return self.date

	def set_date(self, date):
		self.date = date

	# BODY

	def get_body(self):
		return self.body

	def set_body(self, body):
		self.body = body.lower()

	# SOURCEs

	def get_source_url(self):
		return self.source_url

	def set_source_url(self, source_url):
		self.source_url = source_url

	# IMAGE URL
		
	def get_image_url(self):
		return self.image_url

	def set_image_url(self, image_url):
		self.image_url = image_url

	# CLUSTER NUMBER
		
	def get_cluster_number(self):
		return self.cluster_number

	def set_cluster_number(self, cluster_number):
		self.cluster_number = cluster_number

	# JSON

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

class News:

	def __init__(self, feed_url = "", title = "", date = "", source = "", nid = 0, testata = "", description = "", image_url = "", source_url = "", cluster_number = 0):

		self.set_feed_url(feed_url)
		self.set_title(title)
		self.set_date(date)
		self.set_source(source)

		self.nid = nid
		self.testata = testata
		self.description = description
		self.image_url = image_url
		self.source_url = source_url

	# NEWS - ID

	def get_nid(self):
		return self.nid

	def set_nid(self, nid):
		self.nid = nid

	# URL

	def get_feed_url(self):
		return self.feed_url

	def set_feed_url(self, feed_url):
		self.feed_url = feed_url

	# TITLE

	def get_title(self):
		return self.title

	def set_title(self, title):
		self.title = title.lower()

	# DATE

	def get_date(self):
		return self.date

	def set_date(self, date):
		self.date = date

	# SOURCEs

	def get_source(self):
		return self.source

	def set_source(self, source):
		self.source = source

	# TESTATA

	def get_testata(self):
		return self.testata

	def set_testata(self, testata):
		self.testata = testata

	# DESCRIPTION

	def get_description(self):
		return self.description

	def set_description(self, description):
		self.description = description.lower()

	# IMAGE URL
		
	def get_image_url(self):
		return self.image_url

	def set_image_url(self, image_url):
		self.image_url = image_url

	# SOURCE
		
	def get_source_url(self):
		return self.source_url

	def set_source_url(self, source_url):
		self.source_url = source_url

	# CLUSTER NUMBER

	def get_cluster_number(self):
		return self.cluster_number

	def set_cluster_number(self, category = None):

		global clusters
		global array_clusters

		# Default value
		self.cluster_number = -1

		# HOTFIX
		if category == None and self.feed_url != "" and clusters == {}:
			array_clusters = [] # Reset array_clusters

		if category != None:

			self.cluster_number = categories.index(category)
			array_clusters[self.cluster_number] += [self.nid]

		elif category == None and self.feed_url != "":

			for cluster in clusters:
				if self.feed_url in cluster:
					self.cluster_number = clusters[self.feed_url]
					break

			if self.cluster_number == -1:
				self.cluster_number = len(clusters)
				clusters[self.feed_url] = self.cluster_number
				array_clusters += [[self.nid]]

	# SERIALIZE

	def wrap_news(self):
		wrapper = WrapNews()
		wrapper.set_feed_url(self.get_feed_url())
		wrapper.set_nid(self.get_nid())
		wrapper.set_title(self.get_title())
		wrapper.set_date(self.get_date())
		wrapper.set_testata(self.get_testata())
		wrapper.set_body(self.get_description())
		wrapper.set_source_url(self.get_source_url())
		wrapper.set_image_url(self.get_image_url())
		wrapper.set_cluster_number(self.get_cluster_number())
		return wrapper

	def to_JSON(self):
		return json.dumps(self.wrap_news(), default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

def check_if_file_exists(path, msg = ""):
	if not os.path.exists(path):
		print "Sorry, the following file does not exist:", path
		if msg != "":
			print msg
		return False
	return True

def load_stop_words():
	global stop_words
	f = open(STOP_WORDS_PATH, "r")
	line = f.readline()
	while line:
	    stop_words += [line.rstrip('\n')]
	    line = f.readline()
	f.close()
	# return stop_words

# Lists the set of sources from which the news are taken
def get_list_testata(list_news):
	for news in list_news:
		print(str(news.get_testata()))

def parse_news(url, title, date, source, nid, category = None):
	news = News(url, title, date, source, nid)
	news.set_cluster_number(category)
	parser = MyHTMLParser(news)
	return news.wrap_news();

def removePuntuaction(s):
	for c in string.punctuation:
		s = s.replace(c, ' ')
	s = re.sub('\s+', ' ', s).strip()
	return s

def clean_title(title):
	title = re.sub(' - .*', ' ', title)
	title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
	return title

def remove_stop_words(list_news):

	global stop_words
	if stop_words == []:
		load_stop_words()

	def remove_stop_words_from_string(st,stop_words):

		ret = []
		for ss in st.split():

			if type(ss) is unicode:
					ss = unicodedata.normalize('NFKD', ss).encode('ascii','ignore')

			if ss not in stop_words:
				ret += [ss]

		st = " ".join(ret)
		for c in string.punctuation:
			st = st.replace(c, ' ')
		st = re.sub('\s+', ' ', st).strip()
		return st

	jsc = SparkContext(appName="Jsonizer: Remove stop words")
	l = jsc.parallelize(fromNewsToTuple(list_news))
	l = l.map(lambda n:(n[0],remove_stop_words_from_string(n[1],stop_words),remove_stop_words_from_string(n[2],stop_words))).collect()
	list_news = reassemblyNews(list_news,l)
	jsc.stop()
	return list_news

def create_news_json_file(list_news, output = JSON_NEWS_PATH):
	
	count = len(list_news)
	f = open(output, 'w')
	f.write('[')
	for news in list_news:
		f.write(str(news.to_JSON()))
		count -= 1
		if(count > 0):
			f.write(',')
	f.write(']')
	f.close()
	return list_news

# Parses a txt file stored in GOOGLE_NEWS_PATH which contains a set of news.
# Each news have 4 lines: url, title, date, source.
# source_path is the path of the txt file as results of the Crawler.py
# remove_stop_word is a flag that tells whether the stop words have to be removed from the news or not.
def parse_news_file(source_path = GOOGLE_NEWS_PATH, remove_stop_word = False, category = None, start_nid = 0):

	nid = start_nid
	list_news = []
	file_exists = check_if_file_exists(source_path)

	if file_exists:

		# File which contains all the news taken from the crawler..
		# Each news is a set of 4 lines: 
		#	1)	URL
		#	2)	Title
		#	3)	Date
		#	4)	HTML source code
		newsFile = open(source_path, "r")
		print "Parsing news in", source_path

		while True:

			# Read lines about a single news..
			url = newsFile.readline().rstrip('\n')
			title = newsFile.readline().rstrip('\n')
			date = newsFile.readline().rstrip('\n')
			source = newsFile.readline().rstrip('\n')

			# Check emptyness..
			if not url or not title or not source: break

			# Converts a news into an object News..
			title = clean_title(title)
			news = parse_news(url, title, date, source, nid, category)
			list_news += [news]
			nid += 1

		# It is no needed to order the list..
		newsFile.close()

		# Remove duplicates
		list_news = clean_duplicates(list_news, category)

		# Check if stop words have to be removed..
		if remove_stop_word:
			list_news = remove_stop_words(list_news)

	return list_news

def fromNewsToTuple(list_news):
	ret = []
	for n in list_news:
		ret += [(n.get_nid(), n.get_title(), n.get_body())]
	return ret

def reassemblyNews(list_news, tuples):

	# Sort tuples by nid
	tuples.sort(key=lambda n: n[0])

	for i in range(0, len(tuples)):

		nid, t, b = tuples[i]

		if list_news[i].get_nid() == nid:
			list_news[i].set_title(t)
			list_news[i].set_body(b)

	return list_news

# It returns an ORDERED list of News() which are stored in GOOGLE_NEWS_PATH.
def getListNewsFromTxt(source_path = GOOGLE_NEWS_PATH, remove_stop_word = False):

	# Return value: list of News()
	list_news = parse_news_file(source_path = source_path, remove_stop_word = remove_stop_word, category = None, start_nid = 0)
	list_news.sort(key=lambda n: n.get_nid())
	return list_news

# It returns an ORDERED list of News() which are stored in JSON_NEWS_PATH.
# Crawler.py downloads news from Google and store them in a txt file in GOOGLE_NEWS_PATH.
# Might be the case that the json file JSON_NEWS_PATH is not consistent with respect to the one in GOOGLE_NEWS_PATH
# Some news might not be converted in json and stored in JSON_NEWS_PATH. Hence, need to do it manually.
def getListNewsFromJson(json_path = JSON_NEWS_PATH, source_path = GOOGLE_NEWS_PATH, remove_stop_word = False):

	# Retrieves news from GOOGLE_NEWS_PATH
	list_news_from_crawler = getListNewsFromTxt(source_path, remove_stop_word)
	list_news_from_json = []

	# Check whether the json file JSON_NEWS_PATH exists..
	json_exists = check_if_file_exists(json_path)

	if not json_exists:

		# The whole news stored in GOOGLE_NEWS_PATH have to be converted into json ones and stored in JSON_NEWS_PATH
		print "Converting", source_path, "into", json_path, "..."
		start_time = time.time()
		create_news_json_file(list_news_from_crawler)
		elapsed = time.time() - start_time
		print len(list_news_from_crawler), "news have been imported from", JSON_NEWS_PATH
		print "Done in ", elapsed
		return list_news_from_crawler # It's the same as the one stored in the json file

	# Retrieve news from JSON_NEWS_PATH..
	newsFile = open(json_path, 'r')
	list_news = json.loads(newsFile.read())	# Will be a list of json, need to convert it in WrapNews.

	for news in list_news:

		n = WrapNews()
		n.set_nid(int(news['nid']))
		n.set_title(news['title'])
		n.set_testata(news['testata'])
		n.set_date(news['date'])
		n.set_body(news['body'])
		n.set_source_url(news['source_url'])
		n.set_image_url(news['image_url'])
		n.set_cluster_number(int(news['cluster_number'])) # da cambiare
		n.set_feed_url(news['feed_url'])
		list_news_from_json += [n]

	newsFile.close()

	# Get the nids form lists
	list_nids_from_crawler = [n.get_nid() for n in list_news_from_crawler]
	list_nids_from_json = [n.get_nid() for n in list_news_from_json]

	# Get the intersection
	nids_news_to_add = list(set(list_nids_from_crawler).difference(set(list_nids_from_json)))

	# Sort
	list_news_from_json.sort(key=lambda n: n.get_nid())

	# Check if there are news which are stored in the txt file but not stored yet in the json file..
	if nids_news_to_add != []:

		nids_news_to_add.sort()
		news_to_add = [] 

		# nids_news_to_add is ordered, need to scan GOOGLE_NEWS_PATH only once.. => O(n)
		search = nids_news_to_add.pop(0)

		for n in list_news_from_crawler:
			if n.get_nid() == search:
				news_to_add += [n]
				if nids_news_to_add != []:
					search = nids_news_to_add.pop(0)
				else:
					break

		# Remove last line of the file, and add the news which are stored in news_to_add
		newsFile = open(json_path, "r+")
		newsFile.seek(0, os.SEEK_END)
		pos = newsFile.tell() - 1
		while pos > 0 and newsFile.read(1) != "\n":
		    pos -= 1
		    newsFile.seek(pos, os.SEEK_SET)

		if pos > 0:
		    newsFile.seek(pos, os.SEEK_SET)
		    newsFile.truncate()

		newsFile.write('\n},')
		count = len(news_to_add)
		for news in news_to_add:
			newsFile.write(str(news.to_JSON()))
			count -= 1
			if(count > 0):
				newsFile.write(',')
		newsFile.write(']')
		newsFile.close()

		list_news_from_json += news_to_add

	# Remove duplicates
	list_news_from_json = clean_duplicates(list_news_from_json)

	# Check if stop words have to be removed..
	if remove_stop_word:
		list_news_from_json = remove_stop_words(list_news_from_json)

	# Remove news which belong to the first page..
	list_news_from_json = remove_news_which_belong_to_first_page(list_news_from_json)

	return list_news_from_json

# Remove news which have URL_FIRST_PAGE_NEWS as feed_url
def remove_news_which_belong_to_first_page(list_news):
	return filter(lambda n: n.get_feed_url() != URL_FIRST_PAGE_NEWS, list_news)

# Joins two lists of news which belong to different txt files (input_path_1 and input_path_2) in a single json output file
# which will be stored in output_path.
def mergeFromTxtToJson(input_path_1, input_path_2, output_path, remove_stop_word = False,):

	l1 = getListNewsFromTxt(input_path_1, remove_stop_word)
	l2 = getListNewsFromTxt(input_path_2, remove_stop_word)

	last_nid = l1[-1].get_nid()

	for e in l2:
		e.set_nid(e.get_nid() + last_nid)

	result = l1 + l2
	create_news_json_file(result, output_path)

	return result

# Removes duplicates from a list of news
def clean_duplicates(list_news, category = None):

	list_with_no_duplicates = []
	jsc = SparkContext(appName="Jsonizer: Remove duplicates")
	l = jsc.parallelize(define_tuple_title_nid_from_listnews(list_news))
	no_duplicates = l.map(lambda n: (n[0], n[1])).reduceByKey(lambda nid1, nid2 : nid1).collect()
	jsc.stop()

	no_duplicates_nids = [nid for title, nid in no_duplicates]
	for n in list_news:
		if n.get_nid() in no_duplicates_nids:
			list_with_no_duplicates += [n]


	number_of_duplicates = len(list_news) - len(no_duplicates_nids)
	print number_of_duplicates, "news have been removed as duplicates."

	# Remove duplicates also from clusters..
	if category != None and number_of_duplicates > 0:
		array_clusters[categories.index(category)] = list(set(array_clusters[categories.index(category)]).intersection(set(no_duplicates_nids)))
		array_clusters[categories.index(category)].sort()

	return list_with_no_duplicates

# Defines a tuple (title, nid) for each news belong to list_news.
# Used as lambda function for a map operation in spark.
def define_tuple_title_nid_from_listnews(list_news):
	ret = []
	for n in list_news:
		ret += [(n.get_title(), n.get_nid())]
	return ret

def getNewsFromTxtByCategories(remove_stop_word = False, output_json_path = "crawler/categories/merge.json"):

	list_news = []
	source_paths = []

	for c in categories:
		path = CATEGORIES_FOLDER + c.lower().replace(" ", "_") + ".txt"
		if check_if_file_exists(path):
			source_paths += [path]

	start_nid = 0
	for i in range(0, len(source_paths)):
		if list_news != []:
			start_nid = list_news[-1].get_nid() + 1
		list_news += parse_news_file(source_paths[i], remove_stop_word, categories[i], start_nid)

	print "Merging categories sources into", output_json_path, "..."
	start_time = time.time()
	create_news_json_file(list_news, output_json_path)
	elapsed = time.time() - start_time
	print len(list_news), "news have been merged."
	print "Done in ", elapsed
	return list_news

l = getListNewsFromJson()
get_list_testata(l);