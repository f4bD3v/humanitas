
import Orange, orange, orngAssoc, csv

"""Project: Humanitas
   Developer: Alexander Bueser 
   Summary:	This class generates the association rules"""


class assoc:


		
	def startMining(self):
		data = orange.ExampleTable("data/final.csv") 
		data = data.select(range(47))

		minSupport = 0.75


		rules = orange.AssociationRulesInducer(data, support = minSupport) 
		print "%i rules with support higher than or equal to %5.3f found." % (len(rules), minSupport) 
		print orngAssoc.sort(rules, ["support", "confidence"])

		print orngAssoc.printRules(rules[:], ["support", "confidence"]) 


