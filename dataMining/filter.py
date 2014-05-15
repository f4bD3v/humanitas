
import csv,operator

"""	Project: 	Humanitas
	Editor: 	Alexander Buesser	
	Summary:	 
												"""




with open('main/2404Output.csv', 'rU') as csvFile: 
	spamreader = csv.reader(csvFile, delimiter = ',')
	a = open('main/OutputSorted.csv', 'w')
	b = csv.writer(a)
	spamreader = list(csv.reader(csvFile, delimiter = ','))

	for row in spamreader:
		if row[-1] == '': 
			row[-1] = 'NA'
		row = [w.replace('/', '') for w in row] 
		row = [w.replace('(', '') for w in row] 
		row = [w.replace(')', '') for w in row]
		row = [w.replace('v7', '') for w in row]
		row = [('NA' if len(w) == 0 else w) for w in row]

		b.writerow(row)
