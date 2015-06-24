import json
import re
import os.path	# files management and checks
from html.parser import HTMLParser
from html.entities import name2codepoint # for html cha

GOOGLE_NEWS_PATH = "newsG.txt"

class MyHTMLParser(HTMLParser):

	def __init__(self, news):

		HTMLParser.__init__(self)

		self.count_a = 0;
		self.count_font = 0;
		self.current_tag = ""

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

		for tag_name,value in attrs:

			# Immagine
			if tag == 'img' and tag_name == "src" and self.count_a == 1:
				self.news.set_image_url(value)

			# URLs
			if tag == 'a' and tag_name == "href" and self.count_a == 1:
				self.news.set_source_url(value)

	def handle_data(self, data):

		# TESTATA
		if self.current_tag == "font":
			print("è un font! ",data,self.count_font )
			if self.count_font == 5:
				self.news.set_testata(data)	
			elif self.count_font == 6:
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
	print(news.to_JSON())

def parse_news_file():

	if not os.path.exists(GOOGLE_NEWS_PATH):
		print("Sorry, no news to parse.")
	else:

		newsFile = open(GOOGLE_NEWS_PATH, "r")

		url = newsFile.readline()
		title = newsFile.readline().rstrip('\n')
		source = newsFile.readline().rstrip('\n')

		parse_news(url,title,source)

		newsFile.close();

parse_news_file()