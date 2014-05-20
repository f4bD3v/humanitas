#---------------------------------
#Joseph Boyd - joseph.boyd@epfl.ch
#---------------------------------

from bs4 import BeautifulSoup
from urllib2 import urlopen
import csv

BASE_URL = 'http://www.inflation.eu'
PAGE = '/inflation-rates/india/historic-inflation/cpi-inflation-india.aspx'
headings = ['inflation', '(monthly basis) inflation', 'inflation (yearly basis)', 'inflation']

FIRST_YEAR = 1999

def main():
    html = urlopen(BASE_URL + PAGE).read()
    soup = BeautifulSoup(html, 'lxml')
    data_links = set([BASE_URL + li['href'] for li in soup.findAll('a', 'tabledatalink')])

    csvfile = open('inflation_data.csv', 'wb')
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(headings)

    for link in data_links:
        print 'Retrieving data from %s ...'%(link)
        html = urlopen(link)
        soup = BeautifulSoup(html, 'lxml')
        odd_rows = soup.findAll('', 'tabledata1') ; even_rows = soup.findAll('', 'tabledata2')
        for i in range(len(odd_rows)):
            odd_row = [','.join(val.findAll(text=True)).encode('utf8').replace('\xc2\xa0', '')
                   for val in odd_rows[i].findAll('td')]
            even_row = [','.join(val.findAll(text=True)).encode('utf8').replace('\xc2\xa0', '')
                   for val in even_rows[i].findAll('td')]
            csv_writer.writerow([odd_row[0], odd_row[1], odd_row[3], odd_row[4]])
            csv_writer.writerow([even_row[0], even_row[1], even_row[3], even_row[4]])

    csvfile.close()

if __name__ == '__main__':
    main()
