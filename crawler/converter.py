
from crawlerFromGoogle import get_testata_source_and_write_on_file
import jsonizer
import parserino

newsFile = open("newsG.txt", "r")
nid = 0
while True:

	url = newsFile.readline().rstrip('\n')
	title = newsFile.readline().rstrip('\n')
	date = newsFile.readline().rstrip('\n')
	source = newsFile.readline().rstrip('\n')

	if not url or not title or not source: break

	news = jsonizer.News(nid = nid, title = title, date = date, body = source, feed_url = url)
	parser = parserino.ParserNews(news)

	get_testata_source_and_write_on_file(news)
	
	print("News parsata :" + str(nid))
	

	nid+=1

	