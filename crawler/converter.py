
from crawlerFromGoogle import parse_news_from_google
import jsonizer
import parserino
import time

newsFile = open("newsG.txt", "r")
nid = 0
while True:

	url = newsFile.readline().rstrip('\n')
	title = newsFile.readline().rstrip('\n')
	date = newsFile.readline().rstrip('\n')
	source = newsFile.readline().rstrip('\n')

	if not url or not title or not source: break

	news = jsonizer.News(nid = nid, title = title, date = date, body = source, feed_url = url)

	if parse_news_from_google(news):
		print(str(nid), "has been parsed!")
		nid+=1
		time.sleep(4)