#!/usr/bin/env python2

import urllib2
import shutil
import re
import sys
import datetime
from lxml import etree

usage_str = """
This scripts downloads daily food prices from http://m.pip.kementan.org/index.php (Indonesia).

Provide date in DD/MM/YYYY format.

Example:

    ./download_indonesia_prices.py 15/03/2013
"""

def download_table(date):
    """Download price table for a given date"""

    main_url = 'http://m.pip.kementan.org/index.php'

    params = 'laporan=LHK-01&tanggal=%s&bulan=%s&tahun=%s&pilihlaporan=View+Laporan' % (date.day, date.month, date.year)

    req = urllib2.Request(main_url, params)
    response = urllib2.urlopen(req)
    html_code = response.read()

    regex = re.compile(r'<div id="content" align="center">.*(<table.+</table>)', re.DOTALL)
    match = regex.search(html_code)
    if not match:
        print "ERROR: table not detected"
        sys.exit(1)
    table_html = match.group(1)

    # Remove commas
    table_html = re.sub(r'(?<=\d),(?=\d)', '', table_html)

    table = etree.XML(table_html)
    rows = iter(table)
    actual_headers = [col.text for col in next(rows)]
    # TODO: translate this bullshit ;)
    headers = ['Dried Grain Harvest', 'Dry unhusked', 'Rice Medium', 'Rice Premium', 'Corn', 'Local soybean', 'Local Peanuts', 'Green Beans', 'Cassava', 'Sweet potato', 'Cassava spindles']
    print "; ".join(headers), "\n"
    

    # Print table
    for row in rows:
        if all(v.text is None for v in row):
            continue
        print ('''"%s"''') % row[0].text,
        for col in row[1:]:
            print col.text,
        print 

def parse_date(date_string):
    """Check date"""

    match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date_string)
    if not match:
        sys.exit("ERROR: invalid date")
    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    return datetime.date(year, month, day)

def usage():
    print usage_str

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)

    date_string = sys.argv[1]
    date = parse_date(date_string)
    download_table(date)

