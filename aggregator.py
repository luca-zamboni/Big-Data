
from pyspark.mllib.clustering import KMeans, KMeansModel
from pyspark import SparkContext
import itertools
from random import shuffle
import random
import sys
import test_clustering as ts
from math import sqrt
from numpy import arange,array,ones,linalg
from pylab import plot,show
from scipy import stats
import time
import numpy as np
# from sklearn import cluster
# import networkx as nx
import matplotlib.pyplot as plt
import os
from loadnews import loadNews
from loadnews import load_stop_words
#import rake

sc = None

N_SHINGLES = 7
THRESHOLD_SIMILARITY = 0.999
THRESHOLD_DEAGGREGATION = 0.0000
THRESHOLD_AGGREGATION = 2
N_PERM = 1000
THRESHOLD_COUNT = 2

NUM_LINER_FITTING  = 5

FACTOR_CLUSTER = 2

BASE_STR_JOIN = " "

shingles = []
shinglesCount = {}

distanceMatrix = []

STOP_WORDS_PATH 	= "stopword.txt"

def asd(s):
	print(s)

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

def jcSig(l1,l2):
	andL = 0.0
	orL = 0.0
	for i in range(0,len(l1)):
		if l1[i] >= 1 and l2[i] >= 1:
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
		av = 0.0
		for nid1 in g1:
			for nid2 in g2:
				#print(nid1,nid2)
				av += distanceMatrix[nid1][nid2] 
				#print(distanceMatrix[nid1][nid2])

		av = av / (len(g1) * len(g2))
		smoothing = 1 #- 1.0/(len(g1) * len(g2))
		if av * smoothing < dist:

			closer = (g1,g2)
			dist = av

	return dist,closer

def getCloserGroupsRandom(groups,distanceMatrix):
	closer = (None,None)
	dist = 9.0
	# Search closer groups
	for g1,g2 in list(itertools.combinations(groups,2)):
		av = 0

		nid1 = random.choice(g1)
		nid2 = random.choice(g2)
		av = distanceMatrix[nid1][nid2] 

		if av < dist:

			closer = (g1,g2)
			dist = av

	return dist,closer


def getAggregatedWithClustering(signatureMatrix,groups,list_clusters):

	# Instantiating distance matrix
	distanceMatrix = [[] for i in range(0,len(signatureMatrix))]
	for i in range(0,len(distanceMatrix)):
		distanceMatrix[i] = [1.0 for y in range(0,len(signatureMatrix))]

	# print(signatureMatrix)
	# Generation distance matrix
	for (nid1,l1),(nid2,l2) in list(itertools.combinations(signatureMatrix.items(),2)):
		sim = jcSig(l1,l2)
		distanceMatrix[nid1][nid2] = (1.0 - sim)

	dist = 0
	# MERGE GROUPS till aggregation
	while dist < THRESHOLD_AGGREGATION and len(groups) > 1:
		dist,(g1,g2) = getCloserGroupsMean(groups,distanceMatrix)
		groups += [g1+g2]
		groups.remove(g1)
		groups.remove(g2)
		print(dist,groups)
		#print(dist,ts.get_purity_index(list_clusters,groups))

	return groups

def transformInRealMatrix(matrix):
	ret = [[] for i in range(0,len(matrix))]
	for i in matrix:
		ret[i] += matrix[i]
	return ret

def clusterKMeanSpark(matrix,k):
	m = transformInRealMatrix(matrix)
	sc = SparkContext(appName="Jsonizer: Remove stop words")
	parsedData = sc.parallelize(m)
	y = []
	x = []
	clustersControl = range(k,k+1)
	for kc in clustersControl:
		clusters = KMeans.train(parsedData, kc, maxIterations=50000,runs=200, initializationMode="k-means||",epsilon=0.0001)
		clu = []

		def error(point,clust):
		    center = clust.centers[clust.predict(point)]
		    return sqrt(sum([x**2 for x in (point - center)]))


		WSSSE = parsedData.map(lambda point: error(point,clusters)).reduce(lambda x, y: x + y)
		for n in m:
			clu += [clusters.predict(np.array(n))]

		x += [kc]
		y += [WSSSE]

		#print(kc,WSSSE)

	#plt.plot(x,y)
	#plt.ylabel('some numbers')
	#plt.show()

	ret = [[] for i in range(0,max(clu)+1)]
	for i in range(0,len(clu)):
		ret[clu[i]] += [i]
	sc.stop()
	return ret

# def getKmeanCluster(matrix):

# 	m = transformInRealMatrix(matrix)
# 	score = 0
# 	oldscore = 0
# 	for kc in range(19,20):
# 		k_means = cluster.KMeans(n_clusters=kc, n_init=len(shingles))
# 		k_means.fit(m)
# 		clu = k_means.predict(m)
# 		ret = [[] for i in range(0,max(clu)+1)]
# 		for i in range(0,len(clu)):
# 			ret[clu[i]] += [i]
# 		print("\n Clus:" + str(kc))

# 	ret = [[] for i in range(0,max(clu)+1)]
# 	for i in range(0,len(clu)):
# 		ret[clu[i]] += [i]
# 	return ret
	
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
			if shi in sh:
				matrix[nid] += [1]
				#matrix[nid] += [sh.count(shi)]
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
				if matrix[n][cell] >= 1:
					if n in signatureMatrix:
						signatureMatrix[n] += [cell]
					else:
						signatureMatrix[n] = [cell]
					break;

	return signatureMatrix

### REMOVE shingles with count < n
def removeShinglesLowCount(matrix,n = THRESHOLD_COUNT):
	global shingles
	l = len(shingles)
	temp = []
	for i in range(0,l):
		count = 0
		for k in matrix:
			if matrix[k][i] >= 1:
				count += 1

		if count <= n :
			temp += [i]

	for j in temp[::-1]:
		for k in matrix:
			del matrix[k][j]
		del shingles[j]


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

	for i in range(4,5):
	
		clust = i
		retNum = 30

		print("Starting LDA with clusters n:" + str(i))
		os.system("./run-lda.sh " + str(clust) + " " + str(retNum) + "")

		topic = getTopics(clust)
		groups,prob = getGroupsFromLda(topic,texts)

		#print(i,prob)

		groups = [g for g in groups if len(g) >=1]

	return groups

#maxZeroooosJaccardiano = 0
#maxZeroooosNid = None
#maxZeroooosNid2 = None
#for nid1 in g:
#	tempMaxZerosNid2 = None
#	tempZerossJaccardiano = 0
#	for nid2 in g:
#		if jcSig(matrix[nid1],matrix[nid2]) <= THRESHOLD_DEAGGREGATION:
#			tempMaxZerosNid2 = nid2
#			tempZerossJaccardiano += 1

#	if tempZerossJaccardiano > maxZeroooosJaccardiano:
#		maxZeroooosJaccardiano = tempZerossJaccardiano
#		maxZeroooosNid = nid1
#		maxZeroooosNid2 = tempMaxZerosNid2
		#if maxZeroooosJaccardiano >= 1:
		#	asd((True,maxZeroooosNid,maxZeroooosNid2))
		#	return True,maxZeroooosNid,maxZeroooosNid2

	#print(nid1,maxZeroooosNid,maxZeroooosJaccardiano)

#print(maxZeroooosNid,maxZeroooosJaccardiano)
#if maxZeroooosJaccardiano > 0:
#	return True,maxZeroooosNid,maxZeroooosNid2

def isAFalse(g,matrix):


	for nid1,nid2 in list(itertools.combinations(g,2)):
		if jcSig(matrix[nid1],matrix[nid2]) <= THRESHOLD_DEAGGREGATION:
			return True,nid1,nid2

	return False,0,0

def splittalo(g,matrix):
	b,n1,n2 = isAFalse(g,matrix)
	if b:
		g1 = [n1]
		g2 = [n2]
		for nid in g:
			if nid != n1 and nid != n2:
				sim1 = 0.0
				sim2 = 0.0
				for tmp in g1:
					sim1 += jcSig(matrix[n1],matrix[nid])
				for tmp in g1:
					sim2 += jcSig(matrix[n2],matrix[nid])


				if sim1 / len(g1) > sim2 / len(g2):
					g1 += [nid]
				else:
					g2 += [nid]

		ret = []
		if isAFalse(g1,matrix)[0]:
			ret += splittalo(g1,matrix)
		else:
			ret += [g1]
		if isAFalse(g2,matrix)[0]:
			ret += splittalo(g2,matrix)
		else:
			ret += [g2]

		return ret

	return [g]
		

def dissassemblalo(matrix,groups):

	toDisassemble = []

	sc = SparkContext(appName="Jsonizer: Remove stop words")
	parrGroup = sc.parallelize(groups)
	groups = parrGroup.map(lambda g:splittalo(g,matrix)).collect()[0]
	sc.stop()
	
	#for i in range(0,len(groups)):
	#	g = groups[i]

		### prova
	#	if isAFalse(g,matrix)[0]:
	#		newG = splittalo(g,matrix)
	#		del groups[i]
	#		groups += newG

	#	if isAFalse(g,matrix)[0]:
	#		newG = splittalo(g,matrix)
	#		del groups[i]
	#		groups += newG

	return groups

def getCommonWord(group,matrix):
	#ret = [0.0 for cell in matrix[0]]
	ret = []
	for i in range(0,len(matrix[0])):
		tmp = 0.0
		for nid in group:
			tmp += matrix[nid][i]

		ret += [tmp]
	
	ret = sorted(range(len(ret)), key=lambda i: ret[i])[-3:]
	return ret

def getSimilar(groups,matrix):
	mass = 0
	ret1 = None
	ret2 = None
	for g1,g2 in list(itertools.combinations(groups,2)):
		words1 = set(getCommonWord(g1,matrix))
		words2 = set(getCommonWord(g2,matrix))
		tmp = len(words1 & words2)
		if mass < tmp:
			if tmp > 0:
				return tmp,g1,g2
			mass = tmp
			ret1 = g1
			ret2 = g2
	return mass,ret1,ret2


def clusteringByWord(groups,matrix):

	sim,g1,g2 = getSimilar(groups,matrix)
	while sim > 0:
		sim,g1,g2 = getSimilar(groups,matrix)
		if sim > 0:
			groups.remove(g1)
			groups.remove(g2)
			groups += [g1+g2]
			#print(len(groups))

	return groups

def getRappresentante(groups,matrix):
	ret = []
	for g in groups:
		maxVal = 0.0
		for nid1 in g:
			avSim = 0.0
			for nid2 in g:	
				avSim += jcSig(matrix[nid1],matrix[nid2])
			avSim /= len(g)
			if maxVal < avSim:
				maxVal = avSim
				maxId = nid1
		ret += [(maxId,g)]
	return ret





# MAIN
def main():

	groups = []
	texts = []
	matrix = {}

	#x = open("input-lda/input.txt","w")

	#news = jsonizer.getListNewsFromJson(remove_stop_word = True)
	#news = jsonizer.getNewsFromTxtByCategories()
	#news = jsonizer.test()
	news,clusters = loadNews(True)
	list_clusters = [c[1] for c in clusters.items()]

	#print("Numer of google cluters " + str(len(list_clusters)))

	#print(len(list_clusters),list_clusters)

	#Rake = rake.Rake(STOP_WORDS_PATH)

	for n in news:

		groups += [n.get_nid()]

		#s = (n.get_title() + n.get_body()).lower()
		
		#for i in range(0,1):
		# print("----")
		#try:
			# print(n.get_body())
		#	print(n.get_title())
		#	print("\n")
		#	s = Rake.run(n.get_title().lower());
		#	print s
		#	return
		#except Exception as e:
		#	print(e)
		#	pass
	

		s = (n.get_title()).lower() + " "
		#s += " " + n.get_body()


		#print(n.get_body())

		#print(getShingle(s))
		#for ss in getShingle(s):
		#	x.write(ss + " ")
		#x.write("\n")

		addGlobalShingle(s)
		texts = texts + [(n.get_nid(),s)]

	#x.close()


	#print(len(shingles))
	print("Filling Matrix")
	matrix = fillMatrix(texts)
	#removeShinglesLowCount(matrix)
	#permutations = getRandomPermutation()
	#matrix = getSignatureMatrix(matrix,permutations)
	#print(shingles)
	#print(matrix)

	#graph(matrix)

	groups = [groups]

	#
	#for i in range(0,len(groups)):
		#groups

	print("Disassembling")
	groups = dissassemblalo(matrix,groups)

	print("Riaggregating ")
	#groups = clusteringByWord(groups,matrix)
	#groups = getAggregatedWithClustering(matrix,groups,list_clusters)
	#print(groups)

	print("Rappresenting ")
	rappGroups = getRappresentante(groups,matrix)

	print(rappGroups)

	for nid,g in rappGroups:
		for n in news:
			if n.get_nid() == nid:
				try:
					print(str(len(g)) + " " + str(n.get_title()))
				except:
					pass

	#groups = getKmeanCluster(matrix)
	#groups = degGetLdaGroups(texts)

	#for i in range(23,40):
		#groups = clusterKMeanSpark(signatureMatrix,i)
		#print(groups)
	
		#groups = dissassemblalo(matrix,groups)

	#print(transformInRealMatrix(matrix))
	#print(shinglesCount)

		#print(groups)
		#a,fsc = ts.get_purity_index(list_clusters,groups)
		#print(i,a,fsc)
		#if a > 0.9:
			#print(i)
			#print(groups)

			#print(a,fsc)
			#print("---------------------------------")

	#print(groups)

# CHIAMATA AL MEIN
if __name__ == "__main__":
	main()