
import urllib.request
import xml.etree.ElementTree as ET
import xml
import hashlib
import re
import time

tempnews = []
md5 = {}

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr,' ', raw_html)
  return cleantext

def addToFile(testata,title,testo):
	print("Added news from " + testata)
	with open("newsG.txt", "a") as myfile:
		myfile.write(testata + "\n")
		myfile.write(title + "\n")
		myfile.write(testo + "\n")

def insert(testata,news,RSS):
	for n in news:
		title = n.find('title').text
		title = remove_tags(re.sub('[^A-Za-z0-9\.èòùàù]+', ' ', title).rstrip('\n'))
		title = title.strip()

		testo = n.find('description').text
		if testo is not None and remove_tags(testo).strip().rstrip('\n') != "":

			testo = remove_tags(testo).strip().rstrip('\n')

			
			newsFile = open("newsG.txt", "r")
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
				addToFile(RSS,title,testo)

while(True):
	try:

		feed = []

		response = urllib.request.urlopen("https://news.google.it")
		data = response.read()
		text = data.decode('utf-8')

		aTags = re.findall('<a [^>.]*>Copertura live</a>', text)

		xmls = []
		for a in aTags:
			links = re.findall('href="[^".]*"', a)
			url = "https://news.google.it/" + links[0][7:-1]
			response = urllib.request.urlopen(url)
			data = response.read()
			text = data.decode('utf-8')

			hrefRSS = re.findall('<a .*>.*RSS<\/a>', text)
			tmp = re.findall('href="([^"]*)"', hrefRSS[0])[0].replace("amp;", "");
			RSS = "https://" + tmp[7:]

			#print(RSS)
			
			response = urllib.request.urlopen(RSS)
			data = response.read()
			text = data.decode('utf-8')


			#print(text)

			root = ET.fromstring(text)
			insert("Google",root.iter('item'),RSS)
			time.sleep( 0 )
		

	except Exception: 
		print("Except")
	time.sleep( 120 )