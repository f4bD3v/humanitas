import csv
import json

cities_list = ['kochi', 'hyderabad', 'madurai', 'chandigarh', 'bhadrawati', 'dehradun', 'jamshedpur', 'ballia', 'guwahati', 'bangalore', 'agra', 'durgapur', 'mumbai', 'vadodara', 'patna', 'itanagar', 'kolkata', 'mandi', 'bhopal', 'coimbatore', 'gurgaon', 'chennai', 'rajkot', 'palakkad', 'jammu', 'howrah', 'delhi', 'thiruvananthapuram', 'vijayawada', 'aurangabad', 'jamtara', 'jodhpur', 'srinagar', 'ahmedabad', 'kottayam', 'kota', 'padra', 'pune', 'jaipur', 'nagpur', 'cuttack', 'vellore', 'jalpaiguri', 'ranchi', 'bharuch', 'jalgaon', 'kolhapur', 'solapur', 'ballabhgarh', 'bareilly', 'barnala', 'bilaspur', 'dera bassi', 'gorakhpur', 'kullu', 'lalru', 'panipat', 'rania', 'rohtak', 'chirala', 'machilipatnam', 'mangalore', 'ongole', 'visakhapatnam']

def getArrayFromCsv(csvFileName):
	content = []
	headers = None

	f = open(csvFileName, "rU")
	reader=csv.reader(f)
	for row in reader:
		if reader.line_num == 1:
			"""
			If we are on the first line, create the headers list from the first row
			by taking a slice from item 1  as we don't need the very first header.
			"""
			headers = row[0:]
		else:
			"""
			Otherwise, the key in the content dictionary is the first item in the
			row and we can create the sub-dictionary by using the zip() function.
			We also know that the stabling entry is a comma separated list of names
			so we split it into a list for easier processing.
			"""
			content.append(dict(zip(headers, row[0:])))
	f.close()
	return content

content = getArrayFromCsv("indian-cities1.csv")
cities = []
cities_name = []
for row in content:
	print row["City"]
	if row["City"].lower() in cities_list:
		print '*************'
		cities_name.append(row['City'])
		cities.append({"type": "Feature", "id": row["City"],
			"geometry": { "type": "Point",
			"coordinates": [float(row["Longitude"]), float(row["Latitude"])]}
			})

print cities_name
with open("cities_temp.json", "w") as outfile:
	json.dump(cities, outfile)