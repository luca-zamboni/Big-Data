
import itertools
from random import shuffle
import sys
import jsonizer

import numpy as np
from sklearn import cluster

N_SHINGLES = 4
THRESHOLD_SIMILARITY = 0.0
THRESHOLD_AGGREGATION = 0.92
N_PERM = 1000
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
	return s.split()
	#return [s[i:i + n] for i in range(len(s) - n + 1)]

def getCloserGroupsFurther(groups,distanceMatrix):
	closer = (None,None)
	dist = 9.0
	# Search closer groups
	for g1,g2 in list(itertools.combinations(groups,2)):
		maxDist = 0
		for nid1 in g1:
			for nid2 in g2:
				if maxDist < distanceMatrix[nid1][nid2]:
					maxDist = distanceMatrix[nid1][nid2] 
				#print(distanceMatrix[nid1][nid2])
		if maxDist < dist:

			closer = (g1,g2)
			dist = maxDist

	return dist,closer

def getCloserGroupsCloser(groups,distanceMatrix):
	closer = (None,None)
	dist = 9
	# Search closer groups
	for g1,g2 in list(itertools.combinations(groups,2)):
		minDist = 9
		for nid1 in g1:
			for nid2 in g2:
				if minDist > distanceMatrix[nid1][nid2]:
					minDist = distanceMatrix[nid1][nid2]
				#print(distanceMatrix[nid1][nid2])
		if minDist < dist:

			closer = (g1,g2)
			dist = minDist

	return dist,closer

def getCloserGroupsMean(groups,distanceMatrix):
	closer = (None,None)
	dist = 9.0
	# Search closer groups
	for g1,g2 in list(itertools.combinations(groups,2)):
		av = 0
		for nid1 in g1:
			for nid2 in g2:
				av += distanceMatrix[nid1][nid2] 
				#print(distanceMatrix[nid1][nid2])

		av = av / (len(g1) * len(g2))
		if av < dist:

			closer = (g1,g2)
			dist = av

	return dist,closer


def getAggregatedWithClustering(signatureMatrix,groups):

	# Instantiating distance matrix
	distanceMatrix = [[] for i in range(0,len(signatureMatrix)+1)]
	for i in range(0,len(distanceMatrix)):
		distanceMatrix[i] = [1.0 for y in range(0,len(signatureMatrix)+1)]

	# Generation distance matrix
	for (nid1,l1),(nid2,l2) in list(itertools.combinations(signatureMatrix.items(),2)):
		sim = jaccardForMinHash(l1,l2)
		distanceMatrix[nid1][nid2] = (1 - (sim)) * (1 - (sim))

	dist = 0
	# MERGE GROUPS till aggregation
	while dist < THRESHOLD_AGGREGATION and len(groups) > 1:
		dist,(g1,g2) = getCloserGroupsMean(groups,distanceMatrix)
		groups += [g1+g2]
		groups.remove(g1)
		groups.remove(g2)
		#print(dist,groups)

	return groups

def transformInReamMatrix(matrix):
	ret = [[] for i in range(0,len(matrix))]
	print(ret)
	for i in matrix:
		print(matrix[i])
		ret[i] += matrix[i]
	return ret

	
def getKmeanCluster(matrix):
	m = transformInReamMatrix(matrix)
	n_clusters = 4
	k_means = cluster.KMeans(n_clusters=n_clusters, n_init=len(shingles))
	#k_means.fit(X)
	#values = k_means.cluster_centers_.squeeze()
	
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
		#print(j,end="\r")
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

def getNewsById(nid,news):
	for n in news:
		if n.get_nid() == nid :
			return n


# MAIN
def main():

	groups = []
	texts = []
	matrix = {}

	news = jsonizer.getListNews(remove_stop_word = True)

	for n in news:

		groups += [[n.get_nid()]]

		s = (n.get_title() + "     " + n.get_description()).lower()
		addGlobalShingle(s)
		texts = texts + [(n.get_nid(),s)]

	# TRY TO OPTIMIZE
	#removeShinglesLowCount()

	#print(shingles)

	matrix = fillMatrix(texts)
	permutations = getRandomPermutation()
	signatureMatrix = getSignatureMatrix(matrix,permutations)

	#groups = getAggregatedWithClustering(signatureMatrix,groups)
	groups = getKmeanCluster(matrix)

	print(groups)

	'''err = 0
	for i in range(0,len(groups)):
		gr = ""
		for nid in groups[i]:
			n = getNewsById(nid,news)
			if gr == "":
				gr = n.get_url()
			elif gr != n.get_url():
				print(n.get_url())
				err+=1
	print("Da cavare sta roba errors : " + str(err))'''


# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()
