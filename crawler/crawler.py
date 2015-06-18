
import urllib.request
import xml.etree.ElementTree as ET
import xml
import hashlib
import re
import time

tempnews = []
md5 = {}

def remove_tags(raw_html):
  cleanr =re.compile('<.*?>')
  cleantext = re.sub(cleanr,'', raw_html)
  return cleantext

def addToFile(testata,title,testo):
	print("Added news from " + testata)
	with open("news.txt", "a") as myfile:
		myfile.write(testata + "\n")
		myfile.write(title + "\n")
		myfile.write(testo + "\n")

def insert(testata,news):
	for n in news:
		title = n.find('title').text
		title = remove_tags(re.sub('[^A-Za-z0-9\.èòùàù]+', ' ', title).rstrip('\n'))
		title = title.strip()

		testo = n.find('description').text
		if testo is not None and remove_tags(testo).strip().rstrip('\n') != "":

			testo = remove_tags(testo).strip().rstrip('\n')

			
			newsFile = open("news.txt", "r")
			tempnews = []
			while True:
				testataF = newsFile.readline().rstrip('\n')
				titleF = newsFile.readline().rstrip('\n')
				testoF = newsFile.readline().rstrip('\n')
				if not testataF or not titleF or not testoF: break
				tempnews += [(titleF,testata)]
			newsFile.close();

			found = False
			for n,t in tempnews:
				if n == title and t == testata:
					found = True
					break;
				#print(n + " --- " + title)
			if not found:
				addToFile(testata,title,testo)

while(True):
	feed = open("feed.txt", "r")

	for url in feed:
		url = url.split()
		response = urllib.request.urlopen(url[1])
		data = response.read()
		text = data.decode('utf-8')
		m = hashlib.sha1(text.encode()).hexdigest()

		if(url[0] not in md5 != m or md5[url[0]]):

			root = ET.fromstring(text)
			insert(url[0],root.iter('item'))

	feed.close()
	time.sleep( 5 )