
import itertools

N_SHINGLES = 4
TRESHOLD = 0.07

def jaccard(list1,list2):
	list1 = getShingle(list1)
	list2 = getShingle(list2)
	s1 = set(list1)
	s2 = set(list2)
	return float(len(s1 & s2))/len(s1 | s2)

def getShingle(l):
	s = "".join(l)
	return [s[i:i + N_SHINGLES] for i in range(len(s) - N_SHINGLES + 1)]


def main():
	newsFile = open("newsProva.txt", "r")
	i=4
	texts = []
	groups = []
	while True:
		testataF = newsFile.readline().rstrip('\n')
		realTestataF = newsFile.readline().rstrip('\n')
		titleF = newsFile.readline().rstrip('\n')
		testoF = newsFile.readline().rstrip('\n')
		if not testataF or not titleF or not testoF: break

		groups += [[i]]

		texts = texts + [(i,testoF)]
		i+=4



	for tup in list(itertools.combinations(texts,2)):
		sim = jaccard(tup[0][1].split(),tup[1][1].split())
		#print(sim,tup[0][0],tup[1][0])
		f = True

		if sim > TRESHOLD :

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


			
			
			

			'''for i in range(0,len(groups)):
				if tup[0][0] in groups[i] :
					if tup[1][0] not in groups[i]:
						groups[i] += [tup[1][0]]
					f = False
				if tup[1][0] in groups[i]:
					if tup[0][0] not in groups[i]:
						groups[i] += [tup[0][0]]
					f = False
			if f:
				groups += [[tup[0][0],tup[1][0]]]
		else:
			l = list(set(itertools.chain(*groups)))
			print(tup[0][0],tup[1][0],l)
			if(tup[1][0] not in l):
				groups += [[tup[1][0]]]
			if(tup[0][0] not in l):
				groups += [[tup[0][0]]]
			print(groups)'''


	for g in groups:
		print(sorted(g))


if __name__ == "__main__":
	main()

