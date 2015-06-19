
import re

outF = open("cleanNews.txt","w");
inF = open("news.txt","r")
STOP_WORD = "stopword.txt"
news = []
lastCount = {}

for s in inF:
	news += [s]

def clean(text):
	text = text.lower()
	text = re.sub('[^A-Za-z0-9\.èéòùàì]+', ' ', text)
	text = re.sub('raquo', ' ', text)
	text = re.sub('nbsp+', ' ', text)
	text = re.sub('...altro', ' ', text)
	text = removeStop(text)
	text = text.strip().rstrip('\n')
	return text

def getStopWord():
	with open(STOP_WORD,'r') as f:
		stop = []
		for line in f:
			a = line.split()
			stop += a
		return stop

def removeStop(string):
	ret = ""
	stop = getStopWord()
	for w in string.split():
		if not w in stop:
			ret +=  " " + w
	return ret

def countLastWordTitle():
	i=0
	while i < len(news):
		title = clean(news[i+1]).split()[-4:]
		#print(title)
		for t in title:
			if t in lastCount:
				lastCount[t] += 1
			else:
				lastCount[t] = 1

		i+=3

def getRealTestata(title):
	testata = title.split()[-4:]
	try:
		i = testata.index("...")
		ret = " ".join(testata[i+1:])
	except:
		ret = ""
		for t in testata:
			if lastCount[t] >= 3:
				ret += t + " "
		if ret == "":
			ret = " ".join(testata)

	ret = ret.strip()

	return ret

countLastWordTitle()
i=0
while i < len(news):
	testata = news[i]
	title = news[i+1]
	text = news[i+2]

	if not testata or not title or not text: break

	testata = clean(testata)
	title = clean(title)
	text = clean(text)

	###### ONLY FOR GOOGLE ######
	testata = getRealTestata(title)

	print(testata + "\n" + title + "\n" + text)

	outF.write(testata + "\n" + title + "\n" + text + "\n");

	i+=3