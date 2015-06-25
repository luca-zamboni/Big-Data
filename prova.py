
import itertools
from random import shuffle

N_SHINGLES = 9
THRESHOLD = 0.07
N_PERM = 100

BASE_STR_JOIN = " "

shingles = []

# Jaccard Similarity of 2 list
def jaccard(list1,list2):
	list1 = getShingleList(list1)
	list2 = getShingleList(list2)
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1 & s2))/len(s1 | s2)

def jaccardForMinHash(list1,list2):
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1 & s2))/len(s1 | s2)

# Get shingles of a list of strings
def getShingleList(l):
	s = BASE_STR_JOIN.join(l)
	return getShingle(s)

# Get shingles of a string of length n
def getShingle(s,n = N_SHINGLES):
	return s.split()
	#return [s[i:i + n] for i in range(len(s) - n + 1)]



def getAggregratedGroups(texts,groups):
	# For each Tuple of News
	for tup in list(itertools.combinations(texts,2)):
		sim = jaccardForMinHash(tup[0][1],tup[1][1])
		print(tup[0][0],tup[1][0],sim)
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
				matrix[nid] += [1]
			else:
				matrix[nid] += [0]

def getRandomPermutation():
	permutation = []
	n = len(shingles)
	for j in range(0,N_PERM):
		x = [[i] for i in range(0,n)]
		shuffle(x)
		permutation += [list(itertools.chain(*x))]
	print(len(permutation[0]))
	return permutation

# Getting signature matrix
def getSignatureMatrix(matrix,permutations):
	signatureMatrix = {}
	for n in matrix:
		for p in permutations:
			for cell in p:
				if matrix[n][cell] == 1:
					if n in signatureMatrix:
						signatureMatrix[n] += [cell]
					else:
						signatureMatrix[n] = [cell]
					#print(cell,n)
					break;

	return signatureMatrix

			

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

	print(shingles)

	fillMatrix(matrix,texts)
	permutations = getRandomPermutation()
	signatureMatrix = getSignatureMatrix(matrix,permutations)

	forGroup = []
	for nid in signatureMatrix:
		forGroup += [(nid,signatureMatrix[nid])]
	#getting groups

	groups = getAggregratedGroups(forGroup,groups)

	for g in groups:
		print(sorted(g))

	#for g in signatureMatrix:
		#print(len(signatureMatrix[g]))



# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()
