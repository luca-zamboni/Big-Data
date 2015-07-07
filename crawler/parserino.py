# -*- coding: utf-8 -*-

import re
from html.parser import HTMLParser

# Global variables
# -----------------------------------------------------------------------------

PARSE_TAGS_PATH = "parse.txt"

# -----------------------------------------------------------------------------

class ParserNews(HTMLParser):

	def __init__(self, news):

		HTMLParser.__init__(self)
		self.count_a = 0;
		self.current_tag = ""
		self.looking_for_testata = False
		self.news = news
		self.parse_news()

	def parse_news(self):
		self.news.set_body(re.sub("&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));"," ", self.news.get_body()))
		self.feed(self.news.get_body())

	def handle_starttag(self, tag, attrs):

		self.current_tag = tag
		
		if tag == 'a':
			self.count_a += 1
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
				print("DATA",data)
				self.looking_for_testata = False

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

	def parse(self):


		source = str(self.source_html)
		self.feed(source)

		# try:
		# 	print("try")
		# 	source = self.source_html#.decode('utf-8')
		# 	self.feed(source)
		# 	print("try")
			
		# except Exception as e:
		# 	print("catch")
		# 	try:
		# 		print("catch-try")
		# 		source = self.source_html
		# 		self.feed(source)
		# 		print("catch-try")
		# 	except Exception as exp:
		# 		print("catch-catch")

		# 		source = self.source_html.decode().encode('utf-8')
		# 		# source = self.source_html.decode('ascii')
		# 		self.feed(source)
		# 		print("catch-catch")
		# 	print("catch")

		# self.feed(self.source_html)
		return (self.title, self.body)

	def handle_starttag(self, tag, attrs):

		for tag_name, value in attrs:

			is_body = False
			is_title = False

			if value != None:

				is_body = self.hash_tags['attrtype_body_val'] in value.split(' ')
				is_title = self.hash_tags['attrtype_title_val'] in value.split(' ')

			if not self.inside_title and tag_name == self.hash_tags['attrtype_title'] and is_title:
				self.inside_title = True
				self.tag_title = tag

			if not self.inside_body and tag_name == self.hash_tags['attrtype_body'] and is_body:
				self.inside_body = True
				self.tag_body = tag

	def handle_endtag(self, tag):

		if tag == self.tag_title and self.inside_title:
			self.inside_title = False

		if tag == self.tag_body and self.inside_body:
			self.inside_body = False

	def handle_data(self, data):

		if self.inside_title:
			self.title += data
			# print(data

		if self.inside_body:
			self.body += data
			# print(data
