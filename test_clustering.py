import json

JSON_OUTPUT_PATH = "newsG.json"

# It calculates the purity value of clustering (a set of clusters resulting from the aggregator.py) with respect to the ground (which is given).
# It provides also the value of precision and recall for each cluster in clustering, and finally the value of f-measure.
# Let r = len(clustering) and k = len(ground) then:
# 1) When r = k, a purity value of one indicates perfect clustering.
# 2) When r > k, purity can be one when each of the clusters is a subset of a partition.
# 3) When r < k, purity can never be one, since at least one cluster must contain points from more than one partition.
# F-measure is the harmonic mean of the precision and recall values for each cluster.
# For a perfect clustering, when r = k, the maximum value of the F-measure is one.
# Source from youtube: https://www.youtube.com/watch?v=y48o4MGShXE
# Source from a draft by Cambridge University: http://www.cs.rpi.edu/~zaki/www-new/uploads/Dmcourse/Main/chap18.pdf
def get_purity_index(ground, clustering):

	r = len(clustering)
	k = len(ground)

	precision_array = []	# Precision values for each cluster. NOTE: it is used only for debug, it can be removed.
	precision_i = 0			# Precision values for clustering[i]

	recall_array = []		# Recall values for each cluster. NOTE: it is used only for debug, it can be removed.
	recall_i = 0			# Recall value for clustering[i]

	purity = 0				# Purity value. NOTE: purity_i is equal to precision_i.

	f_measure_i = 0			# F-measure for clustering[i]
	f_measure = 0			# F-measure value

	elements = 0			# Total number of elements in clustering

	# Get the number of elements in the clustering
	for c in clustering:
		elements += len(c)

	# For each cluster in clustering..
	for i in range(0, r):

		max_intersec_ground_index = 0
		max_intersec = len(set(clustering[i]) & set(ground[0]))

		# For each cluster in ground..
		# j starts from 1 (rather than 0) just for an optimization: see 2 lines above.
		for j in range(1, k):

			# Get the max number of elements which belongs both to the cluster[i] and the ground[j]
			intersection = len(set(clustering[i]) & set(ground[j]))

			if (intersection > max_intersec):
				max_intersec = intersection
				max_intersec_ground_index = j

		# Precision of clustering[i]
		precision_i = 1.0 * max_intersec / len(clustering[i])
		precision_array += [precision_i]

		# Recall of clustering[i]
		recall_i = 1.0 * max_intersec / len(ground[max_intersec_ground_index])
		recall_array += [recall_i]

		# Purity
		purity += (1.0 * len(clustering[i]) * precision_i / elements)

		# F-measure
		f_measure_i = (2.0 * precision_i * recall_i) / (precision_i + recall_i)
		f_measure += (f_measure_i / r)

	# Awesome print..
	#print "Precision:"
	#print precision_array
	#print "Recall:"
	#print recall_array
	#print "Purity: ", purity
	#print "F-measure: ", f_measure

	return purity,f_measure

# The maximum matching measure ensures that only one cluster can match with a given partition, unlike purity, where two different clusters may share the same majority partition.
# def get_maximum_matching_index(ground, clustering):

# Just an example..
# ground = 		[[1,2,3,4],[5,6,7,8],[9,10,11,12]]
# clustering = 	[[1,2,3,4],[5,6,7,8],[9,10,11,12]]

# get_purity_index(ground, clustering)