import csv
from assocToFile import assocToFile 
from dataFrame import dataFrame 


"""Project: Humanitas
   Developer: Alexander Bueser 
   About: Main2 is used to create results of all of the cities and the 
   returns are saved ad files to display on the onlien systesm"""

class generateFiles: 

	def generateFiles():
		cities = []

		for i in range(1000): 
			cities.append(""); 
		print "Start Mining Data"

		with open('data/cities.csv', 'rU') as csvFile:
			spamreader = list(csv.reader(csvFile, delimiter = ','))
			for row in spamreader:
				cities.append(row[0]);


		nodup =  list(set(cities))
		nodup.remove("Gangtok")
		nodup.remove("Nagpur")
		nodup.remove("Rajkot")	
		
		df = dataFrame()
		mining = assocToFile()
		
		for i in range(len(nodup)):

			var = nodup[i]
			print var
			if var == "":
				continue
			
			df.organize(var, 12)
			mining.startMining(var)



  


	generateFiles()