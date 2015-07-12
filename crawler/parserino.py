# -*- coding: utf-8 -*-

import re
from html.parser import HTMLParser

accenti = [('&agrave;', 'à'),('&egrave;', 'è'),('&igrave;', 'ì'),('&ograve;', 'ò'),('&ugrave;', 'ù')]

# ParserNews is used to set:
#	- image_url
#	- testata_url
#	- testata
# The parse() method returns True or False
class ParserNews(HTMLParser):

	def __init__(self, news):

		HTMLParser.__init__(self)
		self.count_a = 0;
		self.current_tag = ""
		self.looking_for_testata = False
		self.news = news

	def parse(self):
		try:
			self.news.set_body(re.sub("&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));"," ", self.news.get_body()))
			self.feed(self.news.get_body())
			return True
		except Exception as e:
			print("Exception in ParserNews:", e)
			return False

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

			if tag == 'a' and tag_name == "href":
				p = re.compile("url=(.*)")
				match = p.findall(value)
				if match != []:
					self.news.set_testata_url(match[0])

	def handle_data(self, data):

		# TESTATA
		if self.current_tag == "font":
			if self.looking_for_testata:
				self.news.set_testata(data)
				self.looking_for_testata = False
			elif self.count_font == 4:
				self.news.set_body(data)

# ParserSource is used to get:
#	- title
#	- body
# The parse() method returns (self.title, self.body) or ("","")
class ParserSource(HTMLParser):

	def __init__(self, source_html, hash_tags):

		HTMLParser.__init__(self)
		self.source_html = source_html
		self.hash_tags = hash_tags

		self.title = ""
		self.body = ""

		self.inside_title = False
		self.tag_title = ""
		self.inside_body = False
		self.tag_body = ""

		self.countTitle = 0
		self.countBody = 0

		self.scriptB = False
		self.scriptT = False

	def parse(self):

		try:
			source = str(self.source_html)
			source = clean_accenti(source)
			self.feed(source)
			return (self.title, self.body)
		except Exception as e:
			print("Exception in ParserSource:", e)
			return ("","")

	def handle_starttag(self, tag, attrs):


		is_body = False
		is_title = False

		for tag_name, value in attrs:

			if value != None:

				is_body = self.hash_tags['attrtype_body_val'] in value.split(' ')
				is_title = self.hash_tags['attrtype_title_val'] in value.split(' ')

				is_body = is_body and tag_name == self.hash_tags['attrtype_body']
				is_title = is_title and tag_name == self.hash_tags['attrtype_title']

			if not self.inside_title and is_title:
				self.inside_title = True
				self.tag_title = tag

			if not self.inside_body and is_body:
				self.inside_body = True
				self.tag_body = tag

			if self.inside_title and tag == self.tag_title:
				self.countTitle += 1

			if self.inside_body and tag == self.tag_body:
				self.countBody += 1

		if (tag == "script" or tag == "style" or tag == "metadata") and self.inside_body:
			self.scriptB = True
			# self.inside_body = False

		if (tag == "script" or tag == "style" or tag == "metadata") and self.inside_title:
			self.scriptT = True
			# self.inside_title = False

	def handle_endtag(self, tag):

		if (tag == "script" or tag == "style" or tag == "metadata") and self.scriptB:
			self.scriptB = False
			# self.inside_body = True

		if (tag == "script" or tag == "style" or tag == "metadata") and self.scriptT:
			self.scriptT = False
			# self.inside_title = True

		if tag == self.tag_title and self.inside_title:
			self.countTitle -= 1
			if self.countTitle == 0:
				self.inside_title = False

		if tag == self.tag_body and self.inside_body:
			self.countBody -= 1
			if self.countBody == 0:
				self.inside_body = False

	def handle_data(self, data):

		data = data.rstrip("\t")
		data = data.rstrip("\n")

		if data != "" and self.inside_title and not self.scriptT:
			self.title += data

		if data != "" and self.inside_body and not self.scriptB:
			self.body += data

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr,' ', raw_html)
  return cleantext

def clean_accenti(string):
	for search, replace in accenti:
	    string = string.replace(search, replace)
	return string