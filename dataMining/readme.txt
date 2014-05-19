				read me: Association Rules




Executable

main:		run python main.py to start association algorithm
generateFile:	run python generateFiles.py to create all rules over all cities. results 		in folder results.


Helper Classes

dataFrame: 	slices data and categorizes the variables
assoc:		runs apriori and outputs rules
assocToFile:	saves rules to file
sortDate.sh	sortes files according to Date
filter.py	filters ("/) and replaces missing values with "NA"


Folder 

lib: 		contains orange library
results:	output saved of assocToFile. rules of all cities
data:		input, output and temp files for running the algorithm


Important variables: 

assoc.minSupport -->		sets minimum support 
dataFrame.granularity --> 	specify the granularity of the 								data. min is weekly (comparison between one week and the 				other hence 2), max is seasonal (12 weeks). 



  