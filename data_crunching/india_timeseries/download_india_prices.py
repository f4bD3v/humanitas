#!/usr/bin/env python2

import urllib2
import shutil
import re
import sys
import datetime
import os
from optparse import OptionParser

usage_str = """
This scripts downloads weekly food prices from http://rpms.dacnet.nic.in/Bulletin.aspx in XLS format. 

Usage:
    python2 download_india_prices.py [options]

    -d DATE                 -- download spreadsheet for this date (ensure it is Friday!)
    -r STARTDATE ENDDATE    -- download all spreadsheets in this date range

Examples:

    python2 download_india_prices.py -d 02/03/2012
    python2 download_india_prices.py -r 20/01/2013 20/03/2013
"""

out_dir = 'xls_out'

def download_spreadsheet(date_string):
    """Download weekly prices in XLS and save them to file"""

    main_url = 'http://rpms.dacnet.nic.in/Bulletin.aspx'

    # TODO: check if tokens/base64 values expire or not
    params = '__VIEWSTATE=%2FwEPDwUKLTMyOTA3MjI1Ng9kFgICAQ9kFgQCDQ8QZGQWAWZkAhgPFCsABWQoKVhTeXN0ZW0uR3VpZCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JDc5NWYyNmMxLTc5OTYtNDljNy04ZmNiLTEwMWYyZTVjMDljYQIBFCsAATwrAAQBAGZkFgICAQ9kFgJmD2QWAmYPZBYMAgEPDxYCHgdWaXNpYmxlaGRkAgIPZBYCAgIPFgIeBVZhbHVlBQVmYWxzZWQCAw9kFgJmD2QWAmYPDxYCHwBoZGQCBQ9kFgICAg8WAh8BBQVmYWxzZWQCBg9kFgJmD2QWAmYPZBYEZg8PZBYCHgVzdHlsZQUQdmlzaWJpbGl0eTpub25lO2QCAw9kFgQCAQ8WAh4HRW5hYmxlZGhkAgQPFgIfAQUDMTAwZAIKD2QWAgIBDxYCHwEFBUZhbHNlZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUdUmVwb3J0Vmlld2VyMTpUb2dnbGVQYXJhbTppbWcFF1JlcG9ydFZpZXdlcjE6X2N0bDg6aW1ngH4V0uEh9SSOm1xq3bgJgGyDNgIP96LELxzNCJ%2FutD8%3D&__EVENTVALIDATION=%2FwEWHgLr9e3WDgKkjKiDDgKgwpPxDQKsrPr5DAK896w2Ap6Ss%2BMJAvHkkI8EAveMotMNAu7cnNENAqLH6hoC0veCxAoCjOeKxgYC3YHBwAQCyYC91AwCyIC91AwCp5zChwMCp5z%2BmA0CyI%2B56wYCxNb9oA8CzO7%2BnQkC6MPz%2FQkCvKm9vQwC0vCh0QoC4qOPjw8C9%2FmBmAICstrw7ggC%2Fa2qigkCgoOCmg8CgoOW9QcCgoPa4w062z2PEYfDeoZgfbqdsNPMXUtlCnyUt5wzsv6RVn9PnA%3D%3D&TxtDate=#{TXTDATE}&RadioButtonList1=Food+Items&DDLReportFormat=MS+Excel&Button1=Generate+Report&TxtVolume=XXXX+NO+03&ReportViewer1%3A_ctl3%3A_ctl0=&ReportViewer1%3A_ctl3%3A_ctl1=&ReportViewer1%3A_ctl11=&ReportViewer1%3A_ctl12=quirks&ReportViewer1%3AAsyncWait%3AHiddenCancelField=False&ReportViewer1%3AToggleParam%3Astore=&ReportViewer1%3AToggleParam%3Acollapse=false&ReportViewer1%3A_ctl9%3AClientClickedId=&ReportViewer1%3A_ctl8%3Astore=&ReportViewer1%3A_ctl8%3Acollapse=false&ReportViewer1%3A_ctl10%3AVisibilityState%3A_ctl0=None&ReportViewer1%3A_ctl10%3AScrollPosition=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl2=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl3=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl4=100'

    params = params.replace('#{TXTDATE}', date_string)
    req = urllib2.Request(main_url, params)
    response = urllib2.urlopen(req)

    out_file_name = out_dir + '/' + re.sub('/', '_', date_string) + '.xls'
    print "### Output file:", out_file_name
    myfile = open(out_file_name, 'wb')
    shutil.copyfileobj(response.fp, myfile)
    myfile.close()

def download_range(drange):
    srange, erange = drange
    sdate = validate_date(srange)
    edate = validate_date(erange)
    friday_num = 4
    while sdate.weekday() != friday_num:
        sdate += datetime.timedelta(days=1)
    
    while edate.weekday() != friday_num:
        edate -= datetime.timedelta(days=1)
    
    if sdate > edate:
        sys.exit("ERROR: start date > end date")

    curdate = sdate
    while curdate < edate:
        download_spreadsheet(curdate.strftime("%d/%m/%Y"))
        curdate += datetime.timedelta(days=7)

def validate_date(date_string):
    match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date_string)
    if not match:
        sys.exit("ERROR: invalid date, " + date_string)
    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    date = datetime.date(year, month, day)
    return date

def check_out_dir():
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

def usage():
    print usage_str

def usage_callback(option, opt, value, parser):
    usage()
    sys.exit(1)

if __name__ == "__main__":
    os.chdir(os.path.dirname(sys.argv[0]))
    parser = OptionParser(add_help_option=False)
    parser.add_option("-h", "--help",
                      action="callback", callback=usage_callback)

    parser.add_option("-r", "--range",
                      action="store", nargs=2, dest="drange")

    parser.add_option("-d", "--date",
                      action="store", nargs=1, dest="date")
    
    (options, args) = parser.parse_args()

    check_out_dir()
    if options.date:
        date_str = options.date
        date = validate_date(date_str)
        if date.weekday() != 4:
            sys.exit("ERROR: the date entered is not Friday, too bad")
        download_spreadsheet(date_str)
    elif options.drange:
        download_range(options.drange)
    else:
        usage()
        sys.exit(1)
    print "### Finished."

