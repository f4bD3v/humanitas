from assoc import assoc 
from dataFrame import dataFrame 


"""Project: Humanitas
   Developer: Alexander Bueser """

class main: 

	def main():
		print "Start Mining Data"
		var = raw_input("Please enter a city: ")
		


		df = dataFrame()
		mining = assoc()
		df.organize(var)
		mining.startMining()



  


	main()