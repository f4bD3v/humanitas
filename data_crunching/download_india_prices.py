#!/usr/bin/env python2

import urllib
import urllib2
import shutil
import re
import sys
import datetime

usage_str = '''
This scripts downloads weekly food prices from http://rpms.dacnet.nic.in/Bulletin.aspx in XLS format. 
'''

def download_spreadsheet(date_string):
    main_url = 'http://rpms.dacnet.nic.in/Bulletin.aspx'

    params = '__VIEWSTATE=%2FwEPDwUKLTMyOTA3MjI1Ng9kFgICAQ9kFgQCDQ8QZGQWAWZkAhgPFCsABWQoKVhTeXN0ZW0uR3VpZCwgbXNjb3JsaWIsIFZlcnNpb249NC4wLjAuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iNzdhNWM1NjE5MzRlMDg5JDc5NWYyNmMxLTc5OTYtNDljNy04ZmNiLTEwMWYyZTVjMDljYQIBFCsAATwrAAQBAGZkFgICAQ9kFgJmD2QWAmYPZBYMAgEPDxYCHgdWaXNpYmxlaGRkAgIPZBYCAgIPFgIeBVZhbHVlBQVmYWxzZWQCAw9kFgJmD2QWAmYPDxYCHwBoZGQCBQ9kFgICAg8WAh8BBQVmYWxzZWQCBg9kFgJmD2QWAmYPZBYEZg8PZBYCHgVzdHlsZQUQdmlzaWJpbGl0eTpub25lO2QCAw9kFgQCAQ8WAh4HRW5hYmxlZGhkAgQPFgIfAQUDMTAwZAIKD2QWAgIBDxYCHwEFBUZhbHNlZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WAgUdUmVwb3J0Vmlld2VyMTpUb2dnbGVQYXJhbTppbWcFF1JlcG9ydFZpZXdlcjE6X2N0bDg6aW1ngH4V0uEh9SSOm1xq3bgJgGyDNgIP96LELxzNCJ%2FutD8%3D&__EVENTVALIDATION=%2FwEWHgLr9e3WDgKkjKiDDgKgwpPxDQKsrPr5DAK896w2Ap6Ss%2BMJAvHkkI8EAveMotMNAu7cnNENAqLH6hoC0veCxAoCjOeKxgYC3YHBwAQCyYC91AwCyIC91AwCp5zChwMCp5z%2BmA0CyI%2B56wYCxNb9oA8CzO7%2BnQkC6MPz%2FQkCvKm9vQwC0vCh0QoC4qOPjw8C9%2FmBmAICstrw7ggC%2Fa2qigkCgoOCmg8CgoOW9QcCgoPa4w062z2PEYfDeoZgfbqdsNPMXUtlCnyUt5wzsv6RVn9PnA%3D%3D&TxtDate=#{TXTDATE}&RadioButtonList1=Food+Items&DDLReportFormat=MS+Excel&Button1=Generate+Report&TxtVolume=XXXX+NO+03&ReportViewer1%3A_ctl3%3A_ctl0=&ReportViewer1%3A_ctl3%3A_ctl1=&ReportViewer1%3A_ctl11=&ReportViewer1%3A_ctl12=quirks&ReportViewer1%3AAsyncWait%3AHiddenCancelField=False&ReportViewer1%3AToggleParam%3Astore=&ReportViewer1%3AToggleParam%3Acollapse=false&ReportViewer1%3A_ctl9%3AClientClickedId=&ReportViewer1%3A_ctl8%3Astore=&ReportViewer1%3A_ctl8%3Acollapse=false&ReportViewer1%3A_ctl10%3AVisibilityState%3A_ctl0=None&ReportViewer1%3A_ctl10%3AScrollPosition=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl2=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl3=&ReportViewer1%3A_ctl10%3AReportControl%3A_ctl4=100'

    params = params.replace('#{TXTDATE}', date_string)

    req = urllib2.Request(main_url, params)
    response = urllib2.urlopen(req)

    out_file_name = re.sub('/', '_', date) + '.xls'
    print "### Output file:", out_file_name
    myfile = open(out_file_name, 'wb')
    shutil.copyfileobj(response.fp, myfile)
    myfile.close()

    print "### Finished."


def validate_date(date_string):
    match = re.match(r'(\d{2})/(\d{2})/(\d{4})', date_string)
    if not match:
        sys.exit("ERROR: invalid date")
    day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
    date = datetime.date(year, month, day)
    if date.weekday() != 4:
        sys.exit("ERROR: the date entered is not Friday, too bad")

def usage():
    print usage_str

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)

    date = sys.argv[1]
    validate_date(date)
    download_spreadsheet(date)

