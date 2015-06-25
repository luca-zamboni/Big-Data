import json
import string
import re
import os.path	# files management and checks
from html.parser import HTMLParser
from html.entities import name2codepoint # for html character

GOOGLE_NEWS_PATH = "crawler/newsG.txt"
STOP_WORDS_PATH = "stopword.txt"
JSON_OUTPUT_PATH = "crawler/news/list_news.json"

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

			# Testata
			if tag == 'font' and tag_name == 'color' and value == '#6f6f6f':
				self.looking_for_testata = True

			# Immagine
			if tag == 'img' and tag_name == "src" and self.count_a == 1:
				self.news.set_image_url(value)

			# URLs
			#if tag == 'a' and tag_name == "href" and self.count_a == 1:
				#self.news.set_source_url(value)

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

	def __init__(self, nid = 0, title = "", testata = "", body = "", source_url = "", image_url = ""):

		self.set_nid(nid)
		self.set_title(title)
		self.set_testata(testata)
		self.set_body(body)
		self.set_source_url(source_url)
		self.set_image_url(image_url)

	def decode_from_utf8(self, string):
		return string
		# return bytes(string, 'utf-8').decode('utf-8','ignore')

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

class News:

	def __init__(self, url = "", title = "", source = "", nid = 0, testata = "", description = "", image_url = "", source_url = ""):

		self.set_url(url)
		self.set_title(title)
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

	def get_url(self):
		return self.url

	def set_url(self, url):
		self.url = url

	# TITLE

	def get_title(self):
		return self.title

	def set_title(self, title):
		self.title = title

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

	# SERIALIZE

	def wrap_news(self):
		wrapper = WrapNews()
		wrapper.set_nid(self.get_nid())
		wrapper.set_title(self.get_title())
		wrapper.set_testata(self.get_testata())
		wrapper.set_body(self.get_description())
		wrapper.set_source_url(self.get_source_url())
		wrapper.set_image_url(self.get_image_url())
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

def parse_news(url, title, source):
	title = clean_title(title)
	title = removePuntuaction(title)
	news = News(url, title, source)
	parser = MyHTMLParser(news)
	return news;

def removePuntuaction(s):
	for c in string.punctuation:
		s = s.replace(c," ")
	return s

def clean_title(title):
	return re.sub(' - .*', ' ', title)

def remove_stop_word_from_string(s,stop_words):
	ret = []
	for ss in s.split():
		if ss not in stop_words:
			ret += [ss]

	return " ".join(ret)


# Parses a file which contains a set of news.
# source_path is the path of the file as results of the crawler.
# remove_stop_word is a flag that tells whether the stop words have to be removed from text or not.
def parse_news_file(source_path = GOOGLE_NEWS_PATH, remove_stop_word = False):

	list_news = []
	nid = 1

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
			source = newsFile.readline().rstrip('\n')
			
			# Check emptyness..
			if not url or not title or not source: break

			# Check if stop words have to be removed..
			if remove_stop_word:
				url = remove_stop_word_from_string(url,stop_words)
				title = remove_stop_word_from_string(title,stop_words)
				source = remove_stop_word_from_string(source,stop_words)

			# Converts a news into an object News..
			news = parse_news(url, title, source)
			news.set_nid(nid)
			nid += 1
			list_news = list_news + [news]
			
		newsFile.close();

	return list_news

# Test function
def check_list_news(list_news):
	print(len(list_news), "news found.")
	for news in list_news:
		if(news.get_description() == "" or news.get_testata() == "" or news.get_source_url() == ""):
			print(str(news.get_nid()))

# Lists the set of sources from which the news are taken
def get_list_testata(list_news):
	for news in list_news:
		print(str(news.get_testata()))

def create_news_files(list_news, path = JSON_OUTPUT_PATH):

	mod = 'w'
	count = len(list_news)

	if not os.path.exists(path):
		mod = 'w'

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

	list_news = parse_news_file(remove_stop_word = False)
	create_news_files(list_news)
	return list_news

getListNews()
