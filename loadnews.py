import json 
from crawler.jsonizer import WrapNews
import string
import unicodedata
import re
from pyspark import SparkContext

JSON_NEWS_PATH 	= "crawler/output.txt"
STOP_WORDS_PATH 	= "stopword.txt"

stop_words = []

def load_stop_words():
	global stop_words
	f = open(STOP_WORDS_PATH, "r")
	line = f.readline()
	while line:
	    stop_words += [line.rstrip('\n')]
	    line = f.readline()
	f.close()

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

	jsc = SparkContext(appName="Jsonizer: Remove stop words")
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

def reassemblyNews(list_news, tuples):

 	# Sort tuples by nid
 	tuples.sort(key=lambda n: n[0])

 	for i in range(0, len(tuples)):

 		nid, t, b = tuples[i]

 		if list_news[i].get_nid() == nid:
 			list_news[i].set_title(t)
 			list_news[i].set_body(b)

# 	return list_news

def loadNews(remove_stop_word = True):

	newsFile = open(JSON_NEWS_PATH, 'r')

	list_json_news = json.loads(newsFile.read())

	list_news = []

	nid = 0

	clusters = {}

	for news in list_json_news:

		n = WrapNews()
		#n.set_nid(int(news['nid']))
		n.set_nid(nid)
		n.set_title(news['title'].lower())
		n.set_testata(news['testata'])
		n.set_date(news['date'])
		n.set_body(news['body'].lower())
		n.set_source_url(news['source_url'])
		n.set_image_url(news['image_url'])
 		n.set_feed_url(news['feed_url'])
 		list_news += [n]

 		if news['feed_url'] in clusters:
 			clusters[news['feed_url']] += [n.get_nid()]
 		else:
 			clusters[news['feed_url']] = [n.get_nid()]

 		nid += 1


 	
 	remove_stop_words(list_news)

 	newsFile.close()

 	return list_news,clusters

 	#for n in list_news:
 		#print(n.get_body())

# CHIAMATA AL MEIN
if __name__ == "__main__":
	loadNews()