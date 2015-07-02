

path = "bckpreDate.txt"
out = "bckpreDate_with_date.txt"

def add_date():

	newsFile = open(path, "r")
	outF = open(out, "w")
		
	while True:

		# Read lines about a single news..
		url = newsFile.readline().rstrip('\n')
		title = newsFile.readline().rstrip('\n')
		source = newsFile.readline().rstrip('\n')

		# Check emptyness..
		if not url or not title or not source: break

		date = "Date"

		outF.write(url+"\n")
		outF.write(title+"\n")
		outF.write(date+"\n")
		outF.write(source+"\n")

	outF.close()
	newsFile.close()


add_date()