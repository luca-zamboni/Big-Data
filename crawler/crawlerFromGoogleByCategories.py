
import urllib.request
import xml.etree.ElementTree as ET
import xml
import hashlib
import re
import time
import os.path	# files management and checks
import threading
import _thread
import sys

tempnews = []
md5 = {}

FOLDER = "crawler/categories/"

def remove_tags(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr,' ', raw_html)
  return cleantext

def addToFile(path, testata, title, date, testo):
	
	print(path)
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
		testo = n.find('description').text

		if testo is not None and remove_tags(testo).strip().rstrip('\n') != "":

			testo = testo.strip().rstrip('\n')

			if not os.path.exists(path):
				addToFile(path, RSS, title, date, testo)
				
			else:

				newsFile = open(path, "r")
				tempnews = []
				
				while True:
					testataF = newsFile.readline().rstrip('\n')
					titleF = newsFile.readline().rstrip('\n')
					dateF = newsFile.readline().rstrip('\n')
					testoF = newsFile.readline().rstrip('\n')
					if not testataF or not titleF or not dateF or not testoF: break
					tempnews += [(titleF,testataF, dateF)]

				newsFile.close();

				found = False
				for n,t,d in tempnews:
					if n == title:
						found = True
						break;

				if not found:
					addToFile(path, RSS, title, date, testo)


def get_mondo(c, text):

	while(True):
		try:

			link = re.findall('href="[^".]*"', re.findall('<a [^>.]*>' + c +'</a>', text)[0])[0][7:-1]
			url = "https://news.google.it/" + link.replace("amp;", "")

			response = urllib.request.urlopen(url)
			data = response.read()
			text = data.decode('utf-8')

			aTags = re.findall('<a [^>.]*>Copertura live</a>', text)

			xmls = []
			for a in aTags:

				lock = _thread.allocate_lock()
				lock.acquire()

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

				insert( str(c) , root.iter('item'), RSS)

				lock.release()
				time.sleep(10)

		except Exception: 
			print("Except")
		time.sleep( 120 )


def main():

	categories = {
		'Esteri': [],
		'Italia': [],
		'Economia' : [],
		'Scienza e tecnologia' : [],
		'Intrattenimento' : [],
		'Sport' : [],
		'Salute' : []
		}

	if (len(sys.argv) != 2):
		print("Usage:")
		print("$ python crawlerFromGoogleByCategories <CATEGORY>")
		print("E.G. $ python crawlerFromGoogleByCategories Esteri")
		print("E.G. $ python crawlerFromGoogleByCategories Scienza_e_tecnologia")
		print("Choose one of them: ")
		for c in categories:
			print(c.replace(" ", "_"))

	else:

		print("Dowloading ", sys.argv[1],"...")
		cat = sys.argv[1].replace("_", " ")

		response = urllib.request.urlopen("https://news.google.it")
		data = response.read()
		text = data.decode('utf-8')

		threading.Thread(target=get_mondo(cat, text)).start()

main()
