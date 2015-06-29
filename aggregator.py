from pyspark.mllib.clustering import KMeans, KMeansModel
from pyspark import SparkContext
import itertools
from random import shuffle
import sys
import jsonizer as js
import test_clustering as ts
from math import sqrt

import numpy as np
from sklearn import cluster

sc = SparkContext(appName="Aggregation")

N_SHINGLES = 4
THRESHOLD_SIMILARITY = 0.0
THRESHOLD_AGGREGATION = 0.95
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
	distanceMatrix = [[] for i in range(0,len(signatureMatrix))]
	for i in range(0,len(distanceMatrix)):
		distanceMatrix[i] = [1.0 for y in range(0,len(signatureMatrix))]

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
		print(dist,groups)

	return groups

def transformInReamMatrix(matrix):
	ret = [[] for i in range(0,len(matrix))]
	for i in matrix:
		ret[i] += matrix[i]
	return ret

def clusterKMeanSaprk(matrix):
	m = transformInReamMatrix(matrix)
	parsedData = sc.parallelize(m)
	clusters = KMeans.train(parsedData, 2500, maxIterations=1000,runs=20, initializationMode="k-means||",epsilon=0.0001)
	clu = []
	def error(point):
	    center = clusters.centers[clusters.predict(point)]
	    return sqrt(sum([x**2 for x in (point - center)]))

	WSSSE = parsedData.map(lambda point: error(point)).reduce(lambda x, y: x + y)
	print("Within Set Sum of Squared Error = " + str(WSSSE))
	for n in m:
		clu += [clusters.predict(np.array(n))]

	print(clu)
	ret = [[] for i in range(0,max(clu)+1)]
	for i in range(0,len(clu)):
		ret[clu[i]] += [i]
	return ret

def getKmeanCluster(matrix):
	m = transformInReamMatrix(matrix)
	score = 0
	oldscore = 0
	#for kc in range(1,20):
	k_means = cluster.KMeans(n_clusters=7, n_init=len(shingles))
	k_means.fit(m)
	clu = k_means.predict(m)
	'''clu = k_means.predict(m)
	print(clu)
	if oldscore == 0:
		oldscore = k_means.score(m)
	else:
		score = oldscore - k_means.score(m)
		print(kc,k_means.score(m))
		oldscore =  k_means.score(m)'''

	ret = [[] for i in range(0,max(clu)+1)]
	for i in range(0,len(clu)):
		ret[clu[i]] += [i]
	return ret
	
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
			matrix[nid] += [sh.count(shi)]
			#if shi in sh:
			#	matrix[nid] += [1]
			#else:
			#	matrix[nid] += [0]
	return matrix


##########    SLOWWWWWW     ##########
def getRandomPermutation():
	permutation = []
	n = len(shingles)
	for j in range(0,N_PERM):
		print(str(j) + "\r")
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

	news = js.getListNews(remove_stop_word = True)

	for n in news:

		groups += [[n.get_nid()]]

		s = (n.get_title() + "     " + n.get_description()).lower()
		addGlobalShingle(s)
		texts = texts + [(n.get_nid(),s)]


	# TRY TO OPTIMIZE
	#removeShinglesLowCount()

	#print(shingles)

	matrix = fillMatrix(texts)
	print("start perm")
	permutations = getRandomPermutation()
	print("end Perm")
	signatureMatrix = getSignatureMatrix(matrix,permutations)

	#groups = getAggregatedWithClustering(signatureMatrix,groups)
	#groups = getKmeanCluster(matrix)
	groups = clusterKMeanSaprk(signatureMatrix)

	ts.get_purity_index(js.array_clusters,groups)

	print(groups)


# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()
