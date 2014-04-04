#!/bin/bash

### Download something first, for example:
# download_india_prices.py -r 01/01/2013 31/12/2013

YEAR=$1
if [ -z "$YEAR" ]
then
    echo "Give the year, dude!"
    exit 1
fi

### Convert to CSV
python2 ../common/xls_to_csv.py .
FILES=xls_out/*${YEAR}.csv

### Format and output
OUTFILE=all_commodities_weekly_india_${YEAR}.csv
echo -n > $OUTFILE
for f in $FILES
do
    python2 ./parse_weekly.py $f >> $OUTFILE
done
