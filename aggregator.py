
from pyspark.mllib.clustering import KMeans, KMeansModel
from pyspark import SparkContext
import itertools
from random import shuffle
import sys
import jsonizer
import test_clustering as ts
from math import sqrt
from numpy import arange,array,ones,linalg
from pylab import plot,show
from scipy import stats
import time
import numpy as np
from sklearn import cluster
import networkx as nx
import matplotlib.pyplot as plt
import os

#sc = SparkContext(appName="Aggregation")
sc = None

N_SHINGLES = 9
THRESHOLD_SIMILARITY = 0.0
THRESHOLD_AGGREGATION = 2
N_PERM = 1000
THRESHOLD_COUNT = 2

NUM_LINER_FITTING  = 5

FACTOR_CLUSTER = 2

BASE_STR_JOIN = " "

shingles = []
shinglesCount = {}

distanceMatrix = []

# Jaccard Similarity of 2 strings
def jaccard(list1,list2):
	list1 = getShingleList(list1)
	list2 = getShingleList(list2)
	return jaccardForMinHash(list1,list2)

def jaccardForMinHash(list1,list2):
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1 & s2))/len(s1 | s2)

def jaccardForList(l1,l2):
	andL = 0.0
	orL = 0.0
	for i in range(0,len(l1)):
		if l1[i] == 1 and l2[i] ==1:
			andL += 1
		if l1[i] == 1 or l2[i] == 1:
			orL += 1
	if orL == 0:
		return 0.0
	return andL/orL

def jaccardForSignature(l1,l2):
	andL = 0.0
	orL = 0.0
	for i in range(0,len(l1)):
		if l1[i] == l2[i]:
			andL += 1
	return andL/len(l1)

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
				av += distanceMatrix[nid1-1][nid2-1] 
				#print(distanceMatrix[nid1][nid2])

		av = av / (len(g1) * len(g2))
		if av < dist:

			closer = (g1,g2)
			dist = av

	return dist,closer


def getAggregatedWithClustering(signatureMatrix,groups):

	# Instantiating distance matrix
	print(len(signatureMatrix))
	distanceMatrix = [[] for i in range(0,len(signatureMatrix))]
	for i in range(0,len(distanceMatrix)):
		distanceMatrix[i] = [1.0 for y in range(0,len(signatureMatrix))]

	# print(signatureMatrix)
	# Generation distance matrix
	for (nid1,l1),(nid2,l2) in list(itertools.combinations(signatureMatrix.items(),2)):
		sim = jaccardForSignature(l1,l2)
		distanceMatrix[nid1-1][nid2-1] =( 1.0 - sim) * (1.0 - sim)

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
	y = []
	x = []
	clustersControl = range(24,25)
	for kc in clustersControl:
		clusters = KMeans.train(parsedData, kc, maxIterations=100000,runs=200, initializationMode="k-means||",epsilon=0.0001)
		clu = []

		def error(point,clust):
		    center = clust.centers[clust.predict(point)]
		    return sqrt(sum([x**2 for x in (point - center)]))


		WSSSE = parsedData.map(lambda point: error(point,clusters)).reduce(lambda x, y: x + y)
		for n in m:
			clu += [clusters.predict(np.array(n))]

	ret = [[] for i in range(0,max(clu)+1)]
	for i in range(0,len(clu)):
		ret[clu[i]] += [i]
	return ret

	

def getKmeanCluster(matrix):
	m = transformInReamMatrix(matrix)
	getDistanceMatrix(matrix)
	score = 0
	oldscore = 0
	for kc in range(1,23):
		k_means = cluster.KMeans(n_clusters=kc, n_init=len(shingles))
		k_means.fit(m)
		clu = k_means.predict(m)
		ret = [[] for i in range(0,max(clu)+1)]
		for i in range(0,len(clu)):
			ret[clu[i]] += [i]
		print("\n Clus:" + str(kc))
		print(ts.get_purity_index(js.array_clusters,ret))

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
	count = 0
	for nid,s in texts:
		sh = getShingleList(s.split())
		matrix[nid] = []
		for shi in shingles:
			count = sh.count(shi) * 1.0
			if shi in sh:
				matrix[nid] += [count / len(sh)]
			else:
				matrix[nid] += [0]
	return matrix


##########    SLOWWWWWW     ##########
def getRandomPermutation():
	permutation = []
	n = len(shingles)
	for j in range(0,N_PERM):
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

def graph(matrix):
	G=nx.Graph()
	for m in matrix:
		for n in matrix:
			for i in range(0,len(matrix[m])):
				if matrix[m][i] >= 1 and matrix[n][i] >= 1:
					G.add_edge(n,m)
	nx.draw_random(G)
	plt.show()

def getLowestProb(topic):
	l = 1.0
	for t in topic:
		for word in t:
			if float(t[word]) < l:
				l = float(t[word])
	return l

def getTopics(n):
	ret = [{} for m in range(0,n)]
	i = 0
	with open("output-lda/output.txt","r") as f:
		for l in f:
			if len(l.split()) == 1:
				i = int(l)
			else:
				ret[i][l.split()[0]] = l.split()[1]
	return ret

def getProb(probs):
	allP = []
	for t in probs:
		t.sort()
		allP += t
	return sum(allP) / float(len(allP))

def getGroupsFromLda(topic,news):
	lowest = getLowestProb(topic) * 0.1
	groups = [[] for t in topic]
	probs = [[] for t in topic]
	for nid,text in news:
		maxProb = 0.0
		max2p = 0.0
		maxTopic = 0
		for i in range(0,len(topic)):
			p = 1.0
			for s in getShingle(text):
				if s in topic[i]:
					p *= float(topic[i][s])
				else:
					p*= lowest
			if p > max2p and p < maxProb:
				max2p = p
			if p > maxProb and p != 1.0:
				maxTopic = i
				max2p = maxProb
				maxProb = p
		print(nid,maxProb,max2p)
		probs[maxTopic] += [maxProb]	
		groups[maxTopic] += [nid]
	prob = getProb(probs)
	return groups,prob

def degGetLdaGroups(texts):

	for i in range(7,8):
	
		clust = i
		retNum = 30

		print("Starting LDA with clusters n:" + str(i))
		os.system("./run-lda.sh " + str(clust) + " " + str(retNum) + "")

		topic = getTopics(clust)
		groups,prob = getGroupsFromLda(topic,texts)

		#print(i,prob)

		groups = [g for g in groups if len(g) >=1]

	return groups

# MAIN
def main():

	groups = []
	texts = []
	matrix = {}

	x = open("input-lda/input.txt","w")

	news = jsonizer.getListNewsFromJson(remove_stop_word = True)
	#news = jsonizer.getNewsFromTxtByCategories()

	for n in news:

		groups += [[n.get_nid()]]

		s = (n.get_title() + n.get_body()).lower()
		#s = (n.get_title()).lower()

		#print(getShingle(s))
		for ss in getShingle(s):
			x.write(ss + " ")
		x.write("\n")

		addGlobalShingle(s)
		texts = texts + [(n.get_nid(),s)]

	x.close()

	

	# TRY TO OPTIMIZE
	#removeShinglesLowCount()

	#print(shingles)

	matrix = fillMatrix(texts)
	#permutations = getRandomPermutation()
	#signatureMatrix = getSignatureMatrix(matrix,permutations)

	#graph(matrix)

	#groups = getAggregatedWithClustering(matrix,groups)
	#groups = getKmeanCluster(matrix)
	#groups = clusterKMeanSaprk(signatureMatrix)
	#groups = degGetLdaGroups(texts)
	
	#print(matrix)
	#print(shinglesCount)

	print(groups)
	print(ts.get_purity_index(jsonizer.array_clusters,groups))

	#print(len(groups))

# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()