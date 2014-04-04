#!/usr/bin/env python2

import re
import sys
import india_data

def usage():
    print """
Usage:
    
    python2 parse_weekly.py [CSVFILE]

Example:

    python2 parse_weekly.py 02_03_2012.csv
    """

def print_line(line):
    # Product name
    if re.search(r'###', line):
        print line

    # Extract cities and prices for the current week
    for match in re.finditer(r'"([^"\d]+)","([\d\.]+)[^\d"]*","[^"]*","[^"]*"', line):
        city = match.group(1)
        price = match.group(2)
        print "\"%s\": %s" % (city, price)

def main(filename):
    f   = open(filename,'r')
    prevline = ''
    all_products = india_data.all_products
    
    for line in f:
        line = line.rstrip()
        if not re.search(r'"[\w\s]+"', line):
            continue

        if line.find('Andhra Pradesh') == -1:
            print_line(prevline)
            prevline = line
            continue
        product = all_products.pop(0)
        if re.search(r'^,"[^"\d]+","', prevline):
            # Previous line belongs to new product
            print_line('##### "' + product + '" #####')
            print_line(prevline)
        else:
            print_line(prevline)
            print_line('##### "' + product + '" #####')
        prevline = line
    print_line(prevline)


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)

    filename = sys.argv[1]
    main(filename)

