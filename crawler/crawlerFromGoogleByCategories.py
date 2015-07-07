
import urllib.request
import xml.etree.ElementTree as ET
import xml
import hashlib
import re
import time
import os.path		# files management and checks
import sys

FOLDER = "crawler/categories/"

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr,' ', raw_html)
  return cleantext

def addToFile(path, testata, title, date, testo):
	
	with open(path, "a+") as myfile:
		myfile.write(testata + "\n")
		myfile.write(title + "\n")
		myfile.write(date + "\n")
		myfile.write(testo + "\n")

	print("Added news in " + path)

def insert(category, news, RSS):

	path = FOLDER + category.lower().replace(" ","_") + ".txt"

	for n in news:

		title = n.find('title').text
		title = remove_tags(re.sub('[^A-Za-z0-9\.èòùàù-]+', ' ', title).rstrip('\n'))
		title = title.strip()

		date = n.find('pubDate').text

		body = n.find('description').text

		if body is not None and remove_tags(body).strip().rstrip('\n') != "":

			body = body.strip().rstrip('\n')

			# Parses url testata
			p = re.compile("url=(.*^\")\">")
			match = p.findall(body)
			if match != []:
				print("Downloading ", match)
				response = urllib.request.urlopen(match)
				data = response.read()
				text = data.decode('utf-8')

				print(text)






			if not os.path.exists(path):
				addToFile(path, RSS, title, date, body)
				
			else:

				newsFile = open(path, "r")
				tempnews = []
				
				while True:
					testataF = newsFile.readline().rstrip('\n')
					titleF = newsFile.readline().rstrip('\n')
					dateF = newsFile.readline().rstrip('\n')
					bodyF = newsFile.readline().rstrip('\n')
					if not testataF or not titleF or not dateF or not bodyF: break
					tempnews += [(titleF,testataF, dateF)]

				newsFile.close();

				found = False
				for n,t,d in tempnews:
					if n == title:
						found = True
						break;

				if not found:
					addToFile(path, RSS, title, date, body)


def get_news_by_category(category, text):

	link = re.findall('href="[^".]*"', re.findall('<a [^>.]*>' + category +'</a>', text)[0])[0][7:-1]
	url = "https://news.google.it/" + link.replace("amp;", "")

	response = urllib.request.urlopen(url)
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
		
		response = urllib.request.urlopen(RSS)
		data = response.read()
		text = data.decode('utf-8')

		root = ET.fromstring(text)

		insert( str(category) , root.iter('item'), RSS)
		time.sleep(5)

	time.sleep(10)


def main():

	categories = [ 'Esteri', 'Italia', 'Economia' , 'Scienza e tecnologia' , 'Intrattenimento' , 'Sport' , 'Salute' ]

	while(True):
		try:

			response = urllib.request.urlopen("https://news.google.it")
			data = response.read()
			text = data.decode('utf-8')
			for category in categories:
				get_news_by_category(category, text)
				time.sleep(20)

		except Exception: 
			print("Except")
		time.sleep(120)

main()
