import csv, datetime, json, calendar

json_regions = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chattisgarh', 'NCT of Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu and Kashmir', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Orissa', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal']
cities_list = ['hyderabad', 'madurai', 'chandigarh', 'bhadrawati', 'dehradun', 'jamshedpur', 'ballia', 'guwahati', 'bangalore', 'agra', 'durgapur', 'mumbai', 'vadodara', 'patna', 'itanagar', 'kolkata', 'mandi', 'bhopal', 'coimbatore', 'gurgaon', 'chennai', 'rajkot', 'palakkad', 'jammu', 'howrah', 'delhi', 'trivandrum', 'vijayawada', 'aurangabad', 'jamtara', 'jodhpur', 'srinagar', 'ahmedabad', 'kottayam', 'kota', 'padra', 'pune', 'jaipur', 'nagpur', 'cuttack', 'vellore', 'jalpaiguri', 'ranchi', 'bharuch', 'jalgaon', 'kolhapur', 'solapur', 'ballabhgarh', 'bareilly', 'barnala', 'bilaspur', 'dera bassi', 'gorakhpur', 'kullu', 'lalru', 'panipat', 'rania', 'rohtak', 'chirala', 'machilipatnam', 'mangalore', 'ongole', 'visakhapatnam']

chingchia_cities = [
	'Amreli',
	'Anandpur Sahib',
	'Asandh',
	'Aurangabad',
	'Azadpur',
	'Balachaur',
	'Ballabhgarh',
	'Banga',
	'Bangalore',
	'Bankura Sadar',
	'Banur',
	'Bareilly',
	'Barnala',
	'Basti',
	'Bethuadahari',
	'Bharuch',
	'Bhawanigarh',
	'Bhuntar',
	'Bilaspur',
	'Bokaro Chas',
	'Boudh',
	'Budalada',
	'Buland Shahr',
	'Bundi',
	'Burdwan',
	'Champadanga',
	'Chirala',
	'Chittorgarh',
	'Dahod',
	'Dera Bassi',
	'Divi',
	'Faizabad',
	'Fatehabad',
	'Gazipur',
	'Gorakhpur',
	'Guntakal',
	'Gurgaon',
	'Hapur',
	'Harda',
	'Himatnagar',
	'Hinjilicut',
	'Jagadhri',
	'Jalandhar City',
	'Jalgaon',
	'Jalpaiguri',
	'Jamshedpur',
	'JodhpurF&V;',
	'Kalna',
	'Kangra',
	'Keonjhar',
	'Keshopur',
	'Kharar',
	'Kolhapur',
	'Kota',
	'Kullu',
	'Kurali',
	'Lalru',
	'Machilipatnam',
	'Mangalore',
	'Modasa',
	'Morbi',
	'Morinda',
	'Nagpur',
	'Najafgarh',
	'Ongole',
	'Padampur',
	'Pandva',
	'Panipat',
	'Paonta Sahib',
	'Patan',
	'Pratapgarh',
	'Pune',
	'Purulia',
	'Raibareilly',
	'Raikot',
	'Rajkot',
	'Raman',
	'Rampur',
	'Ranchi',
	'Rania',
	'Ratia',
	'Rohtak',
	'Sadulshahar',
	'Sahebganj',
	'Sanad',
	'Sangriya',
	'Shahabad',
	'Sirhind',
	'Sirsa',
	'Sitapur',
	'Solapur',
	'Sriganganagar',
	'Thanesar',
	'Thasara',
	'Unnao',
	'Vadhvan',
	'Vadodara',
	'VaranasiGrain',
	'Visakhapatnam',
	'Visnagar',
	'Yamuna Nagar',
	'Zira']

def getArrayFromCsv(csvFileName):
	content = []
	headers = None

	f = open(csvFileName, "rU")
	reader=csv.reader(f)
	for row in reader:
		if reader.line_num == 1:
			headers = row[0:]
		else:
			content.append(dict(zip(headers, row[0:])))
	f.close()
	return content

def getOriginName(lowerName):
	for region in json_regions:
		if region.lower() == lowerName:
			return region

def add_months(sourcedate, months):
	month = sourcedate.month - 1 + months
	year = sourcedate.year + month / 12
	month = month % 12 + 1
	day = min(sourcedate.day,calendar.monthrange(year,month)[1])
	return datetime.datetime(year,month,day)

full_cities = getArrayFromCsv("indian-cities1.csv")

all_regions = []

# for m in map_regions:
# 	if m['state'] not in all_regions:
# 		all_regions.append(m['state'])

cities = []
count = 0
hits = []


# rice_data = getArrayFromCsv("shark_out/shark_out_rice.csv")

# for rice in rice_data:
# 	rice['date_obj'] = datetime.datetime.strptime(rice['date'], '%Y-%m-%d')

# rice_data = sorted(rice_data, key=lambda x: x['date_obj'])

# vals = [[] for x in xrange(len(json_regions))]

# # For js export
# dthandler = lambda obj: (
# 	obj.isoformat()
# 	if isinstance(obj, datetime.datetime)
# 	or isinstance(obj, datetime.date)
# 	else None)

# # Daily
# results = dict(zip(json_regions, vals))
# starttime = datetime.datetime.strptime('2008-1-1', '%Y-%m-%d')
# endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
# timecount = starttime
# loopcount = 0
# ricecount = 0
# while timecount <= endtime:
# 	print '-----------------------'
# 	print timecount
# 	while ricecount < len(rice_data) and rice_data[ricecount]['date_obj'] <= timecount:
# 		rice = rice_data[ricecount]
# 		print '+++++++++++++++'
# 		print rice['date_obj']
# 		print rice['state']
# 		print getOriginName(rice['state'])
# 		if getOriginName(rice['state']) != None:
# 			results[getOriginName(rice['state'])].append(int(rice['num_tweets']))
# 		ricecount += 1

# 	for state in json_regions:
# 		if len(results[state]) == loopcount:
# 			results[state].append(0)

# 	timecount += datetime.timedelta(days=1)
# 	loopcount += 1

# # Monthly
# monthly_results = {}
# for region in json_regions:
# 	monthly_results[region] = {'name': 'rice', 'data': []}
# starttime = datetime.datetime.strptime('2008-1-1', '%Y-%m-%d')
# endtime = datetime.datetime.strptime('2014-5-11', '%Y-%m-%d')
# timecount = starttime
# acount = 0
# while timecount <= endtime:
# 	new_timecount = add_months(timecount, 1)
# 	days = int((new_timecount - timecount).total_seconds() / 3600 / 24)
# 	if acount + days > len(results[json_regions[0]]):
# 		days = len(results[json_regions[0]]) - acount
# 	print '-------days-------'
# 	print days
# 	for region in json_regions:
# 		monthly_results[region]['data'].append([timecount, sum(results[region][acount:acount+days])])
# 	timecount = new_timecount
# 	acount += days

# for region in json_regions:
# 	print region
# 	print monthly_results[region]['data']
# with open("twitter_rice.json", "w") as outfile:
# 	json.dump(results, outfile, default=dthandler)

	# if row["Longitude"] and row["Latitude"]:
	# 	cities.append({"type": "Feature", "id": row["City"],
	# 		"geometry": { "type": "Point",
	# 		"coordinates": [float(row["Longitude"]), float(row["Latitude"])]}
	# 		})

hits = []
count = 0
for c in chingchia_cities:
	if c.lower() in cities_list:
		hits.append(c)
		count += 1
print len(chingchia_cities)
print count
print hits
# print [item for item in chingchia_cities if item not in hits]
# print [item for item in json_regions if item not in hits]
# with open("cities_temp.json", "w") as outfile:
# 	json.dump(cities, outfile)
