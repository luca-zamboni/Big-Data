

path = "bckpreDateTxt.txt"
out = "bckpreDateTxt_with_date.txt"

def add_date():

	newsFile = open(path, "r")
	outFile = open(out, "r")
		
	while True:

		# Read lines about a single news..
		url = newsFile.readline().rstrip('\n')
		title = newsFile.readline().rstrip('\n')
		source = newsFile.readline().rstrip('\n')

		# Check emptyness..
		if not url or not title or not source: break

		date = "Date"

		out.write(url)
		out.write(title)
		out.write(date)
		out.write(source)

	outFile.close()
	newsFile.close()


add_date()