
import Orange, orange, orngAssoc, csv,sys

"""Project: Humanitas
   Developer: Alexander Bueser 
   Summary:	This class generates the association rules. Change minSupport to adjust the support"""


class assoc:


		
	def startMining(self, var, sup):
		data = orange.ExampleTable("data/finalData.csv") 
		#was47
		data = data.select(range(44))

		minSupport = float(sup)	

	
		rules = orange.AssociationRulesInducer(data, support = minSupport, max_item_sets = 30000000) 
	
	
	
		print "%i rules with support higher than or equal to %5.3f found." % (len(rules), minSupport) 
		
		orngAssoc.printRules(rules[:10], ["support", "confidence"]) 

		
		