# -*- coding: utf-8 -*-
import json
import string
import re
import os.path	# files management and checks
from HTMLParser import HTMLParser
#from html.entities import name2codepoint # for html character

GOOGLE_NEWS_PATH = "newsG.txt"
STOP_WORDS_PATH = "stopword.txt"
JSON_OUTPUT_PATH = "newsG.json"

clusters = {} # Dictionary for clusters
array_clusters = [[]] # Array of clusters (e.g. [[1],[2,3,4,5,6],[7,8,9,10]])

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

		self.set_feed_url(feed_url)
		self.set_nid(nid)
		self.set_title(title)
		self.set_testata(testata)
		self.set_date(date)
		self.set_body(body)
		self.set_source_url(source_url)
		self.set_image_url(image_url)
		self.set_cluster_number(cluster_number)

	def decode_from_utf8(self, string):
		return string
		# return bytes(string, 'utf-8').decode('utf-8','ignore')

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
		self.title = self.decode_from_utf8(title)

	# TESTATA

	def get_testata(self):
		return self.testata

	def set_testata(self, testata):
		self.testata = self.decode_from_utf8(testata)

	# DATE

	def get_date(self):
		return self.date

	def set_date(self, date):
		self.date = date

	# BODY

	def get_body(self):
		return self.body

	def set_body(self, body):
		self.body = self.decode_from_utf8(body)

	# SOURCEs

	def get_source_url(self):
		return self.source_url

	def set_source_url(self, source_url):
		self.source_url = self.decode_from_utf8(source_url)

	# IMAGE URL
		
	def get_image_url(self):
		return self.image_url

	def set_image_url(self, image_url):
		self.image_url = self.decode_from_utf8(image_url)

	# CLUSTER NUMBER
		
	def get_cluster_number(self):
		return self.cluster_number

	def set_cluster_number(self, cluster_number):
		self.cluster_number = cluster_number

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
		self.cluster_number = cluster_number

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
		self.title = title

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
		self.description = description

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

	def set_cluster_number(self):

		global clusters
		global array_clusters

		if len(clusters) == 0:
			clusters[self.feed_url] = self.cluster_number = 0
			array_clusters = [[self.get_nid()]]

		else:

			self.cluster_number = -1;
			for cluster in clusters:
				if self.feed_url in cluster:
					self.cluster_number = clusters[self.feed_url]
					break

			if self.cluster_number == -1:
				self.cluster_number = len(clusters)
				clusters[self.feed_url] = self.cluster_number
				array_clusters += [[self.get_nid()]]

			else:
				array_clusters[self.cluster_number] += [self.get_nid()]

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

def load_stop_words():

	stop_words_path = STOP_WORDS_PATH
	stop_words = []
	f = open(stop_words_path, "r")
	line = f.readline()
	while line:
	    stop_words += [line.rstrip('\n')]
	    line = f.readline()
	f.close()
	return stop_words

def parse_news(url, title, date, source):
	news = News(url, title, date, source)
	parser = MyHTMLParser(news)
	return news;

def removePuntuaction(s):
	for c in string.punctuation:
		s = s.replace(c, ' ')
	s = re.sub('\s+', ' ', s).strip()
	return s

def clean_title(title):
	title = re.sub(' - .*', ' ', title)
	title = re.sub('\s+', ' ', title).strip()
	return title

def remove_stop_word_from_string(string, stop_words):
	ret = []
	for ss in string.split():
		if ss not in stop_words:
			ret += [ss]

	string = " ".join(ret)
	string = removePuntuaction(string)
	return string


# Parses a file which contains a set of news.
# source_path is the path of the file as results of the crawler.
# remove_stop_word is a flag that tells whether the stop words have to be removed from text or not.
def parse_news_file(source_path = GOOGLE_NEWS_PATH, remove_stop_word = False):

	list_news = []
	nid = 0

	if not os.path.exists(source_path):
		print("Sorry, no news to parse in ", source_path , ".")
	else:

		# Loads stop words into a variable, for performance purposes
		if remove_stop_word:
			stop_words = load_stop_words()

		# File which contains all the news taken from the crawler..
		# Each news is a set of 3 lines: 
		#	1)	URL
		#	2)	Title
		#	3)	HTML source code
		newsFile = open(source_path, "r")
		
		while True:

			# Read lines about a single news..
			url = newsFile.readline().rstrip('\n')
			title = newsFile.readline().rstrip('\n')
			date = newsFile.readline().rstrip('\n')
			source = newsFile.readline().rstrip('\n')

			# Check emptyness..
			if not url or not title or not source: break

			title = clean_title(title)
			# Check if stop words have to be removed..
			if remove_stop_word:
				# url = remove_stop_word_from_string(url,stop_words)
				title = remove_stop_word_from_string(title,stop_words)
				source = remove_stop_word_from_string(source,stop_words)

			# Converts a news into an object News..
			news = parse_news(url, title, date, source)
			news.set_nid(nid)
			news.set_cluster_number()
			nid += 1
			list_news = list_news + [news]

	return list_news

# Test function
def check_list_news(list_news):
	print(len(list_news), "news found.")
	for news in list_news:
		if(news.get_description() == "" or news.get_date() == "" or news.get_testata() == "" or news.get_source_url() == ""):
			print(str(news.get_nid()))

# Lists the set of sources from which the news are taken
def get_list_testata(list_news):
	for news in list_news:
		print(str(news.get_testata()))

def create_news_files(list_news, path = JSON_OUTPUT_PATH):

	mod = 'w'
	count = len(list_news)

	f = open(path, mod)

	f.write('[')
	for news in list_news:
		f.write(str(news.to_JSON()))
		count -= 1
		if(count > 0):
			f.write(',')
	
	f.write(']')
	f.close()

def getListNews(remove_stop_word = False):

	list_news = parse_news_file(remove_stop_word = remove_stop_word)
	create_news_files(list_news)
	return list_news

# getListNews()
