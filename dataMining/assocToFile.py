import Orange, orange, orngAssoc, csv,sys

"""Project: Humanitas
   Developer: Alexander Bueser 
   Summary:	This class generates the association rules for the file output"""


class assocToFile:


		
	def startMining(self, var):
		data = orange.ExampleTable("data/finalData.csv") 
		#was47
		data = data.select(range(44))

		minSupport = 0.4	

	
		rules = orange.AssociationRulesInducer(data, support = minSupport, max_item_sets = 30000000) 
	
		orig_stdout = sys.stdout
	
		f = open('results/{}_assocrules.txt'.format(var), 'w')
		sys.stdout = f
		print "%i rules with support higher than or equal to %5.3f found." % (len(rules), minSupport) 
		orngAssoc.printRules(rules[:10], ["support", "confidence"]) > f

		sys.stdout = orig_stdout

		f.close()

		
		


