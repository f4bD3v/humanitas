from assoc import assoc 
from dataFrame import dataFrame 


"""Project: Humanitas
   Developer: Alexander Bueser """

class main: 

	def main():
		print "Start Mining Data"
		var = raw_input("Please enter a city: ")
		sup = raw_input("Please enter a support [0.4 - 0.8]: ")
		gran = raw_input("Please enter a granulairty [value between 2 and 12]: ")
		


		df = dataFrame()
		mining = assoc()
		df.organize(var, gran)
		mining.startMining(var,sup)

  


	main()