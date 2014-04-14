#!/usr/bin/env python2

import sys
import datetime
import os
from optparse import OptionParser
from random import randint

usage_str = """
Check missing date ranges for daily data

Usage:
    python2 download_agmarket_daily.py [options]

    -c COMMODITY            -- specify commodity (check at the website!)

Examples:

    python2 check_dates.py -c Rice
"""

csv_out_dir = 'csv_out'

def check_out_dir():
    if not os.path.exists(csv_out_dir):
        sys.exit("No csv_out dir!")

def check_filename(filename):
    return os.path.exists(filename) and os.stat(filename).st_size > 0

def check_date_range(commodity):
    start_date = datetime.date(2005, 1, 1)
    end_date  = datetime.date(2014, 3, 31)
    
    curdate = start_date
    start_range = None
    day_delta = datetime.timedelta(days=1)
    print "### Missing ranges:"
    print "-c", commodity
    while curdate <= end_date:
        filename = commodity + '_' + curdate.strftime("%d_%m_%Y") + '.csv'
        filename = csv_out_dir + '/' + filename
        if check_filename(filename):
            if start_range:
                end_range = curdate - day_delta
                print "-r %s %s" % (start_range.strftime("%d/%m/%Y"), end_range.strftime("%d/%m/%Y"))
                start_range = None
        else:
            if not start_range:
                start_range = curdate
        curdate += day_delta
    if start_range:
        end_range = curdate - day_delta
        print "-r %s %s" % (start_range.strftime("%d/%m/%Y"), end_range.strftime("%d/%m/%Y"))

def usage():
    print usage_str

def usage_callback(option, opt, value, parser):
    usage()
    sys.exit(1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = OptionParser(add_help_option=False)
    parser.add_option("-h", "--help",
                      action="callback", callback=usage_callback)

    parser.add_option("-c", "--commodity",
                      action="store", nargs=1, dest="commodity")
    
    (options, args) = parser.parse_args()

    check_out_dir()
    if not options.commodity:
        usage()
        sys.exit("No commodity given!")
    else:
        commodity = options.commodity
    check_date_range(commodity)
    print "### Finished."

