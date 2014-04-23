#!/bin/bash

COMMODITY=${1:-Rice}

YEARS="2005 2006 2007 2008 2009 2010 2011 2012 2013 2014"


echo "Downloading commodity: $COMMODITY"
for YEAR in $YEARS 
do
    echo -n "Data from year $YEAR, started: " && date
    # In case the download process is interrupted, '|| true' prevents the script from exiting
    python2 download_agmarket_daily.py -c $COMMODITY -r 01/01/$YEAR 31/12/$YEAR || true
done

### Might be useful
OUTFILE_BASE="india_daily_${COMMODITY}_2005-2014"
OUTFILE_CSV="${OUTFILE_BASE}.csv"

echo "date,freq,country,region,product,subproduct,price,tonnes" > $OUTFILE_CSV
cat csv_out/${COMMODITY}_*.csv >> $OUTFILE_CSV

### Zip stuff
zip $OUTFILE_BASE $OUTFILE_CSV
