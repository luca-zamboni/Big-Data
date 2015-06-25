
import itertools
from random import shuffle
import sys
import jsonizer

N_SHINGLES = 5
THRESHOLD_SIMILARITY = 0.07
N_PERM = 100
THRESHOLD_COUNT = 2

BASE_STR_JOIN = " "

shingles = []
shinglesCount = {}

# Jaccard Similarity of 2 strings
def jaccard(list1,list2):
	list1 = getShingleList(list1)
	list2 = getShingleList(list2)
	return jaccardForMinHash(list1,list2)

# Jaccard Similarity of 2 strings
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
	#return s.split()
	return [s[i:i + n] for i in range(len(s) - n + 1)]



def getAggregratedGroups(signatureMatrix,groups):

	distanceMatrix = [[] for i in range(len(signatureMatrix))]
	for i in range(0,len(distanceMatrix)):
		distanceMatrix[i] = [0.0 for y in range(len(signatureMatrix))]

	# For each Tuple of News
	for (nid1,l1),(nid2,l2) in list(itertools.combinations(signatureMatrix.items(),2)):

		sim = jaccardForMinHash(l1,l2)
		
		#distanceMatrix[nid1][nid2] = 1 - sim

		print(nid1,nid2,"\t",sim)

		f = True

		if sim > THRESHOLD_SIMILARITY :

			for i in range(0,len(groups)):
				if nid1 in groups[i] :
					l1 = groups[i]
				if nid2 in groups[i]:
					l2 = groups[i]

			#print(l1+l2)

			try:
				if l1 != l2:
					groups += [l1+l2]
					groups.remove(l1)
					groups.remove(l2)

			except:
				pass
	#print(distanceMatrix)
	#for item in distanceMatrix:
		#print(item[0], ', '.join(map(str, item[1:])))
	return groups
	
def addGlobalShingle(st):
	global shingles
	global shinglesCount
	sh = getShingleList(st.split())
	for s in sh:
		if s not in shingles:
			shingles += [s]
			shinglesCount[s] = 1
		else:
			shinglesCount[s] += 1

# Return the signature matrix far all the singles  
def fillMatrix(texts):
	matrix = {}
	for nid,s in texts:
		sh = getShingleList(s.split())
		matrix[nid] = []
		for shi in shingles:
			if shi in sh:
				matrix[nid] += [1]
			else:
				matrix[nid] += [0]
	return matrix


##########    SLOWWWWWW     ##########
def getRandomPermutation():
	permutation = []
	n = len(shingles)
	for j in range(0,N_PERM):
		print(j,end="\r")
		x = [[i] for i in range(0,n)]
		shuffle(x)	### <<<<<<<<<<< SLOWWWWWWWWWWWWWWWWWWWWWW
		permutation += [list(itertools.chain(*x))]
	return permutation
######## RLY FORKING SLOOOOOOOW #####

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
					break;

	return signatureMatrix

### REMOVE shingles with count < n
def removeShinglesLowCount(n = THRESHOLD_COUNT):
	global shingles
	global shinglesCount
	for sh in shinglesCount:
		if shinglesCount[sh] < n:
			shingles.remove(sh)

# MAIN
def main():

	groups = []
	texts = []
	matrix = {}

	for n in jsonizer.getListNews(remove_stop_word = True):

		groups += [[n.get_nid()]]

		addGlobalShingle(n.get_title() + " " + n.get_description())
		texts = texts + [(n.get_nid(),n.get_description())]

	# TRY TO OPTIMIZE
	#removeShinglesLowCount()

	#print(shingles)

	matrix = fillMatrix(texts)
	permutations = getRandomPermutation()
	signatureMatrix = getSignatureMatrix(matrix,permutations)

	groups = getAggregratedGroups(signatureMatrix,groups)

	for g in groups:
		print(sorted(g))

# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()
