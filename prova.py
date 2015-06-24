
import itertools

N_SHINGLES = 4
THRESHOLD = 0.07

BASE_STR_JOIN = ""

shingles = []

# Jaccard Similarity of 2 list
def jaccard(list1,list2):
	list1 = getShingleList(list1)
	list2 = getShingleList(list2)
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1 & s2))/len(s1 | s2)

# Get shingles of a list of strings
def getShingleList(l):
	s = BASE_STR_JOIN.join(l)
	return getShingle(s)

# Get shingles of a string of length n
def getShingle(s,n = N_SHINGLES):
	return [s[i:i + n] for i in range(len(s) - n + 1)]

def getAggregratedGroups(texts,groups):
	# For each Tuple of News
	for tup in list(itertools.combinations(texts,2)):
		sim = jaccard(tup[0][1].split(),tup[1][1].split())
		#print(sim,tup[0][0],tup[1][0])
		f = True

		if sim > THRESHOLD :

			for i in range(0,len(groups)):
				if tup[0][0] in groups[i] :
					l1 = groups[i]
				if tup[1][0] in groups[i]:
					l2 = groups[i]

			#print(l1+l2)

			try:
				if l1 != l2:
					groups += [l1+l2]
					groups.remove(l1)
					groups.remove(l2)

			except:
				pass
	return groups
	
def addGlobalShingle(st):
	global shingles
	sh = getShingleList(st.split())
	for s in sh:
		if s not in shingles:
			shingles += [s]

def fillMatrix(matrix,texts):
	for nid,s in texts:
		sh = getShingleList(s.split())
		matrix[nid] = []
		for shi in shingles:
			if shi in sh:
				matrix[nid] += [0]
			else:
				matrix[nid] += [1]
			

# MAIN
def main():
	newsFile = open("newsProva.txt", "r")
	i=4
	groups = []
	texts = []
	matrix = {}
	while True:
		testataF = newsFile.readline().rstrip('\n')
		realTestataF = newsFile.readline().rstrip('\n')
		titleF = newsFile.readline().rstrip('\n')
		testoF = newsFile.readline().rstrip('\n')
		if not testataF or not titleF or not testoF: break

		groups += [[i]]

		addGlobalShingle(testoF)
		texts = texts + [(i,testoF)]
		i+=4


	fillMatrix(matrix,texts)

	#getting groups
	groups = getAggregratedGroups(texts,groups)

	for g in groups:
		print(sorted(g))

	
	
	#print(matrix)

# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()
