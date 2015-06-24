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

def parse_news_file(path):

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

			parse_news(url,title,source)


		newsFile.close();

def create_news_files(path):

	if not os.path.exists(path):
		print("Sorry, no news to parse in ", path , ".")
	else:
		strin = '<table border="0" cellpadding="2" cellspacing="7" style="vertical-align:top;"><tr><td width="80" align="center" valign="top"><font style="font-size:85%;font-family:arial,sans-serif"><a href="http://news.google.com/news/url?sa=t&amp;fd=R&amp;ct2=it&amp;usg=AFQjCNGLiCpLOfwJxLlRMrIfOyCLCtI02g&amp;clid=c3a7d30bb8a4878e06b80cf16b898331&amp;cid=52779454240467&amp;ei=ZHqFVYjcGNWoaseAg5gJ&amp;url=http://www.quotidiano.net/austria-suv-contro-passanti-1.1076583"><img src="//t3.gstatic.com/images?q=tbn:ANd9GcRk0XvPCFQ3WrTqXsZhr5JsdJQF0FgPMD4a9SAgfQyDZAnDWfclUEaO_cTMeQIMevsniSBlSAs" alt="" border="1" width="80" height="80"><br><font size="-2">Quotidiano.net</font></a></font></td><td valign="top" class="j"><font style="font-size:85%;font-family:arial,sans-serif"><br><div style="padding-top:0.8em;"><img alt="" height="1" width="1"></div><div class="lh"><a href="http://news.google.com/news/url?sa=t&amp;fd=R&amp;ct2=it&amp;usg=AFQjCNGLiCpLOfwJxLlRMrIfOyCLCtI02g&amp;clid=c3a7d30bb8a4878e06b80cf16b898331&amp;cid=52779454240467&amp;ei=ZHqFVYjcGNWoaseAg5gJ&amp;url=http://www.quotidiano.net/austria-suv-contro-passanti-1.1076583"><b>Austria, con il suv contro la folla: 3 morti Polizia: &quot;Armato, ma non è <b>...</b></b></a><br><font size="-1"><b><font color="#6f6f6f">Quotidiano.net</font></b></font><br><font size="-1">L&#39;autore del folle gesto è un 26enne austriaco di origini bosniache.Il giovane soffre di problemi psichici. Almeno 34 i feriti. Tra le vittime un bimbo di 7 anni e una donna. Austria, uomo si lancia con il suv contro la folla. (Ansa)&nbsp;...</font><br><font size="-1" class="p"></font><br><font class="p" size="-1"><a class="p" href="http://news.google.it/news/story?ncl=dkdCZaFrYIPByEM&amp;ned=it"><nobr><b>altro&nbsp;&raquo;</b></nobr></a></font></div></font></td></tr></table>'
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
		# 	f = open(path_single, "a+")
		# 	f.write(HTMLBeautifier.beautify(source, 4))
		# 	f.close()

		# newsFile.close()


create_news_files(GOOGLE_NEWS_PATH)
# parse_news_file(GOOGLE_NEWS_PATH)



