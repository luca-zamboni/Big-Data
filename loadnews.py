import json 
from crawler.jsonizer import WrapNews
import string
import unicodedata
import re
from pyspark import SparkContext
# from polyglot.text import text

JSON_NEWS_PATH 	= "crawler/output.json"
STOP_WORDS_PATH 	= "stopword.txt"

stop_words = []

MIN_NUM_KEYWORDS = 4

def load_stop_words():
	global stop_words
	f = open(STOP_WORDS_PATH, "r")
	line = f.readline()
	while line:
	    stop_words += [line.rstrip('\n')]
	    line = f.readline()
	f.close()
	return stop_words

def remove_stop_words(list_news):

	global stop_words
	if stop_words == []:
		load_stop_words()

	def removeNumbers(s):
		s = re.sub('[0-9]', ' ', s)
		return s

	def removePuntuaction(s):
		for c in string.punctuation:
			s = s.replace(c, ' ')
		s = re.sub('\s+', ' ', s).strip()
		return s

	def remove_stop_words_from_string(st,stop_words):

		st = removePuntuaction(st)

		ret = []
		for ss in st.split():

			if type(ss) is unicode:
				ss = unicodedata.normalize('NFKD', ss).encode('ascii','ignore')

			if ss not in stop_words:
				ret += [ss]

		st = " ".join(ret)

		st = removeNumbers(st)
		st = re.sub("\t"," ",st)
		st = re.sub("  *"," ",st)

		return st

	jsc = SparkContext(appName="LOADNEWS: Remove stop words")
	l = jsc.parallelize(fromNewsToTuple(list_news))
	l = l.map(lambda n:(n[0],remove_stop_words_from_string(n[1],stop_words),remove_stop_words_from_string(n[2],stop_words))).collect()
	list_news = reassemblyNews(list_news,l)
	jsc.stop()
	return list_news

def fromNewsToTuple(list_news):
 	ret = []
 	for n in list_news:
 		ret += [(n.get_nid(), n.get_title(), n.get_body())]
 	return ret

def formNewsToIdTitleBodyUrl(list_news):
	ret = []
 	for n in list_news:
 		ret += [(n.get_nid(), n.get_title(), n.get_body(), n.get_source_url())]
 	return ret

def reassemblyNews(list_news, tuples):

 	# Sort tuples by nid
 	tuples.sort(key=lambda n: n[0])

 	for i in range(0, len(tuples)):
 		nid, t, b = tuples[i]
 		if list_news[i].get_nid() == nid:
 			list_news[i].set_title(t)
 			list_news[i].set_body(b)

def reassemblyNewsAndSetKeywords(list_news, tuples):

 	# Sort tuples by nid
 	tuples.sort(key=lambda n: n[0])

 	for i in range(0, len(tuples)):
 		nid, keywords = tuples[i]
 		if list_news[i].get_nid() == nid:
 			list_news[i].set_keywords(keywords)


def clean_title(title):
	title = re.sub(' - .*', ' ', title)
	title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
	return title

def get_keywords_from_list_news(list_news):

	def get_keyword_from_string(text):

		keywords = []
		try:
			text = Text(text)
			
			for entity in text.entities:
				for e in entity:
					try:
						k = e.encode('utf-8')
						keywords += [k]
					except Exception as e:
						pass

			#  Are enough keywords to deal with?
			if len(keywords) < MIN_NUM_KEYWORDS:
				return ""

			# Removes duplicate keywords
			no_duplicates = set(keywords)
			keywords = list(no_duplicates)
			keywords = " ".join(keywords).lower()

			for c in string.punctuation:
				keywords = keywords.replace(c, '')

		except Exception as e:
			print "Exception in get_keyword_from_string:", e
			pass

		return ' '.join(keywords.split())

	def get_keyword_from_link(url):

		regex = "(?:http|https)://[\w\d.-]+/([\w\d\/\-]*)"
		try:
			res = re.match(regex, url)
			res = str(res.group(1))
			res = re.sub('\d+', ' ', res)
			res = res.replace('/',' ')
			res = res.replace('_',' ')
			res = res.replace('-',' ')
			res = re.sub(' \w ', ' ', res)
			return " ".join(res.split())
		except Exception as e:
			print e
			pass
		return ""

	def get_keywords(tuple):

		title, body, url = tuple

		keywords = ""

		try:
			title = title.encode('utf-8')
			keywords += get_keyword_from_string(title) + " "
		except Exception as e:
			pass

		try:
			body = body.encode('utf-8')
			keywords += get_keyword_from_string(body) + " "
		except Exception as e:
			pass

		try:
			keywords += get_keyword_from_link(url) + " "
		except Exception as e:
			pass		

		return keywords

	jsc = SparkContext(appName="LOADNEWS: Get keywords")
	l = jsc.parallelize(formNewsToIdTitleBodyUrl(list_news))
	l = l.map(lambda n:(n[0], get_keywords((n[1],n[2],n[3])))).collect()
	list_news = reassemblyNewsAndSetKeywords(list_news,l)
	jsc.stop()

def loadNews(remove_stop_word = True, get_keywords = True):

	newsFile = open(JSON_NEWS_PATH, 'r')

	list_json_news = json.loads(newsFile.read())

	list_news = []

	nid = 0

	clusters = {}

	nnnid = 0

	for news in list_json_news:

		n = WrapNews()
		n.set_nid(nid)
		n.set_title(news['title'].lower())
		n.set_testata(news['testata'])
		n.set_date(news['date'])
		n.set_body(news['body'].lower())
		n.set_source_url(news['source_url'])
		n.set_image_url(news['image_url'])
 		n.set_feed_url(news['feed_url'])

 		if len(news['title'].lower().split()) > 5 :
	 		list_news += [n]

	 		if news['feed_url'] in clusters:
	 			clusters[news['feed_url']] += [n.get_nid()]
	 		else:
	 			clusters[news['feed_url']] = [n.get_nid()]

	 		nid += 1

	 	nnnid += 1

	print("Number of news: " + str((nid+1)))

	if get_keywords:
		get_keywords_from_list_news(list_news)

 	if remove_stop_word:
 		remove_stop_words(list_news)

 	newsFile.close()

 	return list_news,clusters

if __name__ == "__main__":
	loadNews()