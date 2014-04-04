#!/usr/bin/env python2

import re
import sys
import india_data
import os

def usage():
    print """
Usage:
    
    python2 parse_weekly.py [CSVFILE]

Example:

    python2 parse_weekly.py 02_03_2012.csv
    """

# 02/01/2000,week,India,Banda Aceh,milk,condensed,4000.0

date_string = ''
cur_product = ''
def print_line(line):
    # Product name
    #if re.search(r'###', line):
    #    print line

    # Parse product
    match = re.search(r'(\w+)\s*(?:\((.+)\))?', cur_product)
    if not match:
        return
    product_name = match.group(1)
    subproduct_name = match.group(2)
    if not subproduct_name:
        subproduct_name = ''

    # Extract cities and prices for the current week
    for match in re.finditer(r'"([^"\d]+)","([\d\.]+)[^\d"]*","[^"]*","[^"]*"', line):
        city = match.group(1)
        price = match.group(2)
        # print "\"%s\": %s" % (city, price)
        print "%s,week,India,%s,%s,%s,%s" % \
                (date_string, city, product_name, subproduct_name, price)

def main(filename):
    global date_string
    global cur_product
    date_string = re.sub('_', '/', os.path.basename(filename))
    date_string = re.sub('\.\w+$', '', date_string)
    f = open(filename,'r')
    prevline = ''
    all_products = india_data.all_products
    cur_product = ''
    for line in f:
        line = line.rstrip()
        if not re.search(r'"[\w\s]+"', line):
            continue

        if line.find('Andhra Pradesh') == -1:
            print_line(prevline)
            prevline = line
            continue
        if re.search(r'^,"[^"\d]+","', prevline):
            # Previous line belongs to new product
            cur_product = all_products.pop(0)
            print_line(prevline)
        else:
            print_line(prevline)
            cur_product = all_products.pop(0)
        prevline = line
    print_line(prevline)


if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)

    filename = sys.argv[1]
    main(filename)

