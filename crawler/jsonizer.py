import json
import re
import os.path	# files management and checks
from html.parser import HTMLParser
from html.entities import name2codepoint # for html character
from html5print import HTMLBeautifier

GOOGLE_NEWS_PATH = "newsG.txt"

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
			if tag == 'a' and tag_name == "href" and self.count_a == 1:
				self.news.set_source_url(value)

	def handle_data(self, data):

		# TESTATA
		if self.current_tag == "font":
			if self.looking_for_testata:
				self.news.set_testata(data)
				self.looking_for_testata = False
			elif self.count_font == 4:
				txt = self.news.get_description() + data;
				self.news.set_description(txt)

class News:

    def __init__(self, url, title, source, nid = 0, testata = "", description = "", image_url = "", source_url = ""):

        self.url = url
        self.title = title
        self.source = source

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

	# SOURCE

    def get_source(self):
    	return self.source

    def set_source(self, source):
    	self.source = source

    # ----

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

    def to_JSON(self):
    	return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def parse_news(url, title, source):
	news = News(url, title, source)
	parser = MyHTMLParser(news)
	return news;


def parse_news_file(path):

	list_news = []
	nid = 1

	if not os.path.exists(path):
		print("Sorry, no news to parse in ", path , ".")
	else:

		newsFile = open(path, "r")

		while True:

			url = newsFile.readline().rstrip('\n')
			title = newsFile.readline().rstrip('\n')
			source = newsFile.readline().rstrip('\n')
			
			# Check emptyness
			if not url or not title or not source: break

			news = parse_news(url,title,source)
			news.set_nid(nid)
			nid += 1
			list_news = list_news + [news]

		newsFile.close();

	return list_news

def create_news_files(path):

	if not os.path.exists(path):
		print("Sorry, no news to parse in ", path , ".")
	else:
		f = open("news/gen_0.html", "a+")
		f.write(HTMLBeautifier.beautify(strin, 4))
		f.close()

		# newsFile = open(path, "r")
		# count = 0

		# while True:

		# 	count += 1

		# 	url = newsFile.readline().rstrip('\n')
		# 	title = newsFile.readline().rstrip('\n')
		# 	source = newsFile.readline().rstrip('\n')
			
		# 	# Check emptyness
		# 	if not url or not title or not source: break

		# 	path_single = "news/gen_" + str(count) + ".html"
		# 	f = open(path_single, "w")
		# 	f.write(HTMLBeautifier.beautify(source, 4))
		# 	f.close()

		# newsFile.close()


# create_news_files(GOOGLE_NEWS_PATH)
parse_news_file(GOOGLE_NEWS_PATH)
