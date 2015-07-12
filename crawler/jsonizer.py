# -*- coding: utf-8 -*-

import json     	# JSON
import unicodedata 	# For encoding and decoding of json files
import string 		# Strings
import re 			# Regular Expressions
import os
import os.path 		# Files management and checks
import timeit		# Timer
import time

# Spark
# from pyspark import SparkContext

# Global variables
# -----------------------------------------------------------------------------

# GOOGLE_NEWS_PATH 	= "newsG.txt"
# JSON_NEWS_PATH 	= "newsG.json"
# STOP_WORDS_PATH 	= "stopword.txt"
# URL_FIRST_PAGE_NEWS = "https://news.google.it/news?pz=1&cf=all&ned=it&hl=it"
# CATEGORIES_FOLDER = "crawler/categories/"

# -----------------------------------------------------------------------------

class WrapNews:

	def __init__(self, feed_url = "", nid = 0, title = "", testata = "", date = "", body = "", source_url = "", image_url = "", cluster_number = 0, keywords = ""):

		self.set_nid(nid)
		self.set_title(title)
		self.set_testata(testata)
		self.set_date(date)
		self.set_body(body)
		self.set_source_url(source_url)
		self.set_image_url(image_url)
		self.set_cluster_number(cluster_number)
		self.set_feed_url(feed_url)
		self.set_keywords(keywords)

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
		self.title = title

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
		self.body = body

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

	# KEYWORDS

	def get_keywords(self):
		return self.keywords

	def set_keywords(self, keywords):
		self.keywords = keywords

	# JSON

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)

class News:

	def __init__(self, nid = 0, title = "", testata = "", date = "", body = "", feed_url = "", keywords = ""):

		self.nid = nid
		self.title = title
		self.testata = testata
		self.date = date
		self.body = body
		self.feed_url = feed_url
		self.keywords = keywords

		self.testata_url = ""
		self.image_url = ""
		self.cluster_number = 0

	# NEWS - ID

	def get_nid(self):
		return self.nid

	def set_nid(self, nid):
		self.nid = nid

	# TITLE

	def get_title(self):
		return self.title

	def set_title(self, title):
		self.title = title

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
		self.body = body

	# FEED URL

	def get_feed_url(self):
		return self.feed_url

	def set_feed_url(self, feed_url):
		self.feed_url = feed_url

	# IMAGE URL
		
	def get_image_url(self):
		return self.image_url

	def set_image_url(self, image_url):
		self.image_url = image_url

	# TESTATA URL
		
	def get_testata_url(self):
		return self.testata_url

	def set_testata_url(self, testata_url):
		self.testata_url = testata_url

	# CLUSTER NUMBER

	def get_cluster_number(self):
		return self.cluster_number

	def set_cluster_number(self, cluster_number):
		self.cluster_number = cluster_number


	# KEYWORDS

	def get_keywords(self):
		return self.keywords

	def set_keywords(self, keywords):
		self.keywords = keywords

	# SERIALIZE

	def wrap_news(self):
		wrapper = WrapNews()
		wrapper.set_feed_url(self.get_feed_url())
		wrapper.set_nid(self.get_nid())
		wrapper.set_title(self.get_title())
		wrapper.set_date(self.get_date())
		wrapper.set_testata(self.get_testata())
		wrapper.set_body(self.get_body())
		wrapper.set_source_url(self.get_testata_url())
		wrapper.set_image_url(self.get_image_url())
		wrapper.set_cluster_number(self.get_cluster_number())
		wrapper.set_keywords(self.get_keywords())
		return wrapper

	def to_JSON(self):
		return json.dumps(self.wrap_news(), default=lambda o: o.__dict__, sort_keys=True, indent=4, ensure_ascii=False)