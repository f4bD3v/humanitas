#!/bin/bash

COMMODITY=Rice

YEARS="2005 2006 2007 2008 2009 2010 2011 2012 2013 2014"

for YEAR in $YEARS 
do
    python2 download_agmarket_daily.py -c $COMMODITY -r 01/01/$YEAR 31/12/$YEAR || true
done

### Might be useful
# cat csv_out/${COMMODITY}_*.csv > india_${COMMODITY}_2005-2014.csv
