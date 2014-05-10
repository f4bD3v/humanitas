
import Orange, orange, orngAssoc, csv

"""Project: Humanitas
   Developer: Alexander Bueser 
   Summary:	This class generates the association rules"""


class assoc:


		
	def startMining(self):
		data = orange.ExampleTable("data/final.csv") 
		#was47
		data = data.select(range(47))

		minSupport = 0.7	


		rules = orange.AssociationRulesInducer(data, support = minSupport, max_item_sets = 30000) 
		print "%i rules with support higher than or equal to %5.3f found." % (len(rules), minSupport) 
	
		orngAssoc.printRules(rules[:10], ["support", "confidence"]) 
		

