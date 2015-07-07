






def load_stop_words():
	global stop_words
	f = open(STOP_WORDS_PATH, "r")
	line = f.readline()
	while line:
	    stop_words += [line.rstrip('\n')]
	    line = f.readline()
	f.close()

def removePuntuaction(s):
	for c in string.punctuation:
		s = s.replace(c, ' ')
	s = re.sub('\s+', ' ', s).strip()
	return s

# def clean_title(title):
# 	title = re.sub(' - .*', ' ', title)
# 	title = re.sub('\s+', ' ', title).strip().replace(' ...',' ')
# 	return title

def remove_stop_words(list_news):

	global stop_words
	if stop_words == []:
		load_stop_words()

	def remove_stop_words_from_string(st,stop_words):

		ret = []
		for ss in st.split():

			if type(ss) is unicode:
					ss = unicodedata.normalize('NFKD', ss).encode('ascii','ignore')

			if ss not in stop_words:
				ret += [ss]

		st = " ".join(ret)
		for c in string.punctuation:
			st = st.replace(c, ' ')
		st = re.sub('\s+', ' ', st).strip()
		return st

	jsc = SparkContext(appName="Jsonizer: Remove stop words")
	l = jsc.parallelize(fromNewsToTuple(list_news))
	l = l.map(lambda n:(n[0],remove_stop_words_from_string(n[1],stop_words),remove_stop_words_from_string(n[2],stop_words))).collect()
	list_news = reassemblyNews(list_news,l)
	jsc.stop()
	return list_news