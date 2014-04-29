#!/usr/bin/env python2

import urllib2
import shutil
import re
import sys
import datetime
import os
from time import sleep
from optparse import OptionParser
from random import randint
from BeautifulSoup import BeautifulSoup

usage_str = """
This scripts downloads daily retail food prices from http://fcainfoweb.nic.in/PMSver2/Reports/Report_Menu_web.aspx. Results are saved in CSV format to csv_out/ directory.

Usage:
    python2 download_fcainfoweb_daily.py [options]

    -d DATE                 -- download data for this date
    -r STARTDATE ENDDATE    -- download all data in this date range
    -f                      -- use local raw HTML files instead of downloading

Examples:

    python2 download_fcainfoweb_daily.py -d 02/03/2012 
    python2 download_fcainfoweb_daily.py -r 20/01/2013 20/03/2013 -f
"""

csv_out_dir = 'csv_out'
raw_out_dir = 'raw_out'

# Easiest way to get a new cookie is to visit http://fcainfoweb.nic.in/PMSver2/Reports/Report_Menu_web.aspx with your browser and copy the cookie ASP.NET_SessionId here
cookie = 'plq2tt0rsqgoqfdxcjoi5ge0'

def download_data(date_string):
    """Download weekly prices in XLS and save them to file"""

    main_url = 'http://fcainfoweb.nic.in/PMSver2/Reports/Report_Menu_web.aspx'
    params = 'MainContent_ToolkitScriptManager1_HiddenField=%3B%3BAjaxControlToolkit%2C+Version%3D4.1.51116.0%2C+Culture%3Dneutral%2C+PublicKeyToken%3D28f01b0e84b6d53e%3Aen-US%3Afd384f95-1b49-47cf-9b47-2fa2a921a36a%3A475a4ef5%3Aaddc6819%3A5546a2b%3Ad2e10b12%3Aeffe2a26%3A37e2e5c9%3A5a682656%3Ac7029a2%3Ae9e598a9&__EVENTTARGET=&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=nAMJC3oD4TO5c%2B7jRiFrnarRMv05i2lEZsHM0VriP9iU1WnwdzPV8exn2HaN0Pdpqabt5BHGcBqsu1HG28ilmfBCvWehOqVKrbzbTksxY9OriToU7o5%2Fg0Rxp8sEPjxUFYjwo10BjIRiBuuu80dXQR3a023BYcloCxn0OeYH1ceGHo%2BteEphPeiVlgJ3UgGb7D1IB9VToTL3JZ%2Bi8CSwOcwfCZWVcQv8e0JJ5Ylocffk0MtEfgkhxop4ViipoLcy5dplKkzNdskRsgep%2FmvnsU6opOnepjIO0oYberxVoyEjM2zcdggVqXIfmNy%2F1EtcsO9HVGn0cqeVWgYtT3sPR35sQZQMsZjT9bSxXX%2BDlTmTF%2B6rv7ZdQu9OXpwz4Ta9lpAAcZfcU2J2ozk%2FsyDjeVEkkhyJyjmV7tOO4jiKJJzWpE6E9Tf5bs7fSFUzJgOl%2F5F7iOJg0S3pisif1F1a%2B1qVg7uud5p%2F8HatGeDd53eaDPci1yAVGuviyb1fn4KTyubqUbGNK9mQYRIuiMRjwaWBcKdZdLk4z1u1POSm5to%3D&__VIEWSTATEENCRYPTED=&__EVENTVALIDATION=jFcAc4ikcRQ1k1z9MQ6d0udWfcwWaQtx9e3Gx0d7tlPQMpNoCBZmVmk0O5%2FUl5FmUkP2a7%2FQKdKnB8XaqaFUgPgTZ0sZlbpTzTenH%2Fnp4iywH8oi3jGUGMcORoGXaTgF7%2B3t5QIsK4VfiI20cik3DQSGE8P7uhGrccO%2BluXGZWVuopXv40JTT2nExb0ix4gmAcYL6tdryuw61vvqjHkxo04hMKrAoUMTVxjaUyOpeguI0BZdYWk46943BzFetIxjYK%2F4QhYGJrMbdz%2FM%2FfeEajod34m2dqISVmhCEa%2Fu2N8jgqTcsHqDLCwhaNoMiZDA2yW1Yzcli4mAQMGcPqy%2FZd8Ta7ZajpdPlupVtFNK%2BWXrlY54irp8MKRl1IsPyT3y&ctl00%24MainContent%24Ddl_Rpt_type=Retail&ctl00%24MainContent%24Rbl_Rpt_type=Price+report&ctl00%24MainContent%24Ddl_Rpt_Option0=Daily+Prices&ctl00%24MainContent%24Txt_FrmDate=#{TXTDATE}&ctl00%24MainContent%24btn_getdata1=Get+Data'

    params = params.replace('#{TXTDATE}', date_string)
    opener = urllib2.build_opener()
    opener.addheaders.append(('Cookie', 'ASP.NET_SessionId=' + cookie))
    req = opener.open(main_url, params)
    result_html = req.read()
    save_downloaded_data(date_string, result_html)

def save_downloaded_data(date_string, html):
    # Remove some stuff
    html = re.sub(r'<input type="(hidden|submit)"[^>]*>', '', html)
    html = re.sub(r'\s*bordercolor\w*=\w*', '', html)
    html = re.sub(r'\s*align\w*=\w*', '', html)
    html = re.sub(r'<script.+?</script>', '', html, flags=re.DOTALL)

    if html.find('Data does not exist for this date') != -1:
        # No data for the given date
        print ">>> No data for %s" % date_string
        return

    if html.find('Wrong Input or Unauthorised User') != -1:
        # Wrong cookie?
        sys.exit('Session expired, provide a new cookie!')
        return
    # Save raw file
    raw_file_name = get_raw_filename(date_string)
    table = str(html)
    raw_file = open(raw_file_name, "w")
    raw_file.write(table)
    raw_file.close()
    to_csv(date_string, html)
    print "Saved data for %s" % date_string

def get_raw_filename(date_string):
    raw_file_name = raw_out_dir + '/' + re.sub('/', '_', date_string) + '.html'
    return raw_file_name

def to_csv_from_file(date_string):
    raw_filename = get_raw_filename(date_string)
    if not os.path.exists(raw_filename):
        print '>>> No file:', raw_filename
        return
    with open(raw_filename, 'r') as f:
        html = f.read()
        to_csv(date_string, html)

def process_name(name):
    sub_dict = {'T.PURAM': 'Thiruvananthapuram'}
    if name in sub_dict:
        name = sub_dict[name]
    name = name.capitalize()
    return name

def to_csv(date_string, html):
    soup = BeautifulSoup(html)
    tables = soup.findAll('table')
    if len(tables) != 3:
        sys.exit("ERROR: invalid number of tables")

    table = tables[1]
    rows = table.findAll('tr')

    header_row = rows[0]
    headers = header_row.findAll('td')
    products = []
    for product_header in headers[1:]:
        header_text = product_header.getText()
        header_text = re.sub(r'/\s*', '/', header_text)
        header_text = re.sub(r'-\s*|\s*[*@]', '', header_text)
        products.append(header_text)
    nproducts = len(products)

    data_rows = rows[1:]
    out_file_name = csv_out_dir + '/' + re.sub('/', '_', date_string) + '.csv'
    #print "### Output file:", out_file_name
    out_file = open(out_file_name, "w")
    for row in data_rows:
        cells = row.findAll('td')
        if len(cells) < nproducts:
            # Colspan
            continue
        city_name = cells[0].getText()
        if re.search(r'(Maximum|Minimum|Modal) Price', city_name):
            # Final rows
            continue
        city_name = process_name(city_name)
        cells = cells[1:]
        for i in xrange(nproducts):
            product = products[i]
            price = cells[i].getText()
            csv_string = "%s,day,India,%s,%s,,%s,NR\n" % \
                (date_string, city_name, product, price)    
            out_file.write(csv_string)
    out_file.close()

def download_range(drange, from_file):
    srange, erange = drange
    sdate = validate_date(srange)
    edate = validate_date(erange)
    
    if sdate > edate:
        sys.exit("ERROR: start date > end date")

    curdate = sdate
    while curdate <= edate:
        date_string = curdate.strftime("%d/%m/%Y")
        if from_file:
            to_csv_from_file(date_string)
        else:
            download_data(date_string)
        curdate += datetime.timedelta(days=1)

def validate_date(date_string):
    match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date_string)
    if not match:
        sys.exit("ERROR: invalid date, " + date_string)
    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    date = datetime.date(year, month, day)
    return date

def check_out_dir():
    if not os.path.exists(csv_out_dir):
        os.makedirs(csv_out_dir)
    if not os.path.exists(raw_out_dir):
        os.makedirs(raw_out_dir)

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

    parser.add_option("-r", "--range",
                      action="store", nargs=2, dest="drange")

    parser.add_option("-d", "--date",
                      action="store", nargs=1, dest="date")

    parser.add_option("-f", "--from-file",
                      action="store_true", dest="from_file")

    (options, args) = parser.parse_args()

    check_out_dir()
    if options.date:
        date_str = options.date
        date = validate_date(date_str)
        download_data(date_str)
    elif options.drange:
        download_range(options.drange, options.from_file)
    else:
        usage()
        sys.exit(1)
    print "### Finished."

