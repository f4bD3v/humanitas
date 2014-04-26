import csv, math, subprocess
from itertools import izip_longest

"""Project: Humanitas
   Developer: Alexander Bueser 
   Summary:	This class generates the necessary data frame for the association algorithm.
   			Classification of continues variables and sorting are perforemd. Input needs
   			to be in a specific form. See readme.txt form more details"""


class dataFrame: 

	def __init__(self):

		self.test  = [[] for i in range(49)]
		
		self.minArray=[]
		for i in range(99):
			self.minArray.append(10000)

		self.maxArray=[]
		for i in range(99):
			self.maxArray.append(1)

		self.rangeArray=[]
		for i in range(100):
			self.rangeArray.append(range(0,0))

	def classifier(self,value, aRange):

		width = aRange[-1] - aRange[0]
		slot = width/3
		slot1 = aRange[0]+slot
		slot2 = aRange[0] + 2* slot

		small = (aRange[0], slot1-1)
		medium = (slot1, slot2- 1)
		big = (slot2, aRange[-1])
		tag = "UD"

		if value in small: 
			tag = "small"
		if value in medium: 
			tag = "medium"
		if value in big: 
			tag = "big"

		return tag


	def organize(self, city): 	
		"""Big Data Set is filter by City""" 
		isPop = False
		with open('data/outputSorted.csv', 'rU') as csvFile:

			spamreader = list(csv.reader(csvFile, delimiter = ','))
			spamreaderIterator = list(spamreader)

			for row in spamreaderIterator:
				for elements in row:
					if city in elements:
						isPop = True; 


				if isPop == False and "index" not in row[0]: 
					spamreader.remove(row)
					
				else: 
					isPop = False

		a = open('data/output1.csv', 'w')
		b = csv.writer(a)
		for row in spamreader: 
			b.writerow(row)

		a.close()


		"""Performs sort(UniX) on temp file. Unix sort allows us to 
		perform a sort on specific keys of the string. Sort is performed on date"""

		subprocess.call(['./sortDate.sh'])


		with open('data/temp.csv', 'rU') as csvFile:
			reference = list(csv.reader(csvFile, delimiter = ','))

		"""Constructs a price fluctuation range of each product. Needed for classification"""

		with open('data/temp.csv', 'rU') as csvFile:
			finalData = list(csv.reader(csvFile, delimiter = ','))
			for i in range(2,len(reference)):
				for j in range(1, len(reference[i])):
					if reference[i][j] != "NA" and reference[i-1][j] != "NA":
						diff = abs(float(reference[i][j]) - float(reference[i-1][j]))
						#print "{} and {}".format(spamreader[i][j], spamreader[i-1][j])
						self.test[j].append(diff) 
			

			for i in range(0,len(self.test)):
				if self.test[i]:
					self.rangeArray[i+1] = range(int(min(self.test[i])), int(max(self.test[i])) )
					#print "{} and {}".format(min(self.test[i]), max(self.test[i]))


			for i in range(2,len(reference)):
				for j in range(1, len(reference[i])):
					if reference[i][j] != "NA" and reference[i-1][j] != "NA":
						diff = abs(float(reference[i][j]) - float(reference[i-1][j]))
						finalData[i][j] = self.classifier(diff, self.rangeArray[j+1])
			

			"""Base case initialised to medium"""			
			for i in range(1,len(reference[1])):
				finalData[1][i] = "medium"

			
			a = open('data/final.csv', 'w')
			b = csv.writer(a)

			for rows in finalData: 
				b.writerow(rows); 










		











