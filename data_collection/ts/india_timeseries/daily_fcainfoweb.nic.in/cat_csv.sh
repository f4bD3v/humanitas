#!/bin/bash

PRICE_TYPE="retail"
OUTFILE_BASE="india_daily_fcainfo_${PRICE_TYPE}_2009-2014"
OUTFILE_CSV="${OUTFILE_BASE}.csv"

echo "date,freq,country,region,product,subproduct,price,tonnes" > $OUTFILE_CSV
cat csv_out/*csv >> $OUTFILE_CSV
zip $OUTFILE_BASE $OUTFILE_CSV
