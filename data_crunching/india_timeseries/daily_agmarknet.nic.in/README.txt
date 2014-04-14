* download_agmarket_daily.py -- download daily price for a given commodity and a given date range (or date)
* download_all_years.sh -- shell script to automate downloading daily data for a given commodity (it will run a separate job for each year)
* check_dates.py -- script checks missing date ranges for a given commodity


CSV format:

date, period(day/week/month), country, city, product, subproduct, price, tonnes (0.0 => no info)
total: 8 fields
