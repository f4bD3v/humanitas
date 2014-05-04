from bs4 import BeautifulSoup
from urllib2 import urlopen
import csv

BASE_URL = 'http://www.tutiempo.net'
PAGE_1 = '/en/Climate/India/IN.html'
PAGE_2 = '/en/Climate/India/IN_2.html'
headings = ['Year', 'T', 'TM', 'Tm', 'PP', 'V', 'RA', 'SN', 'TS', 'FG', 'TN', 'GR']

def get_category_links(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'lxml')
    location_links = soup.find('div', id='ListadosV4')
    category_links = [BASE_URL + li.a['href'] for li in location_links.findAll('li')]
    return category_links

def main():
    links = get_category_links(BASE_URL + PAGE_1)
    links.extend(get_category_links(BASE_URL + PAGE_2))
    
    csvfile = open('climate_data.csv', 'wb')
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(headings)
    
    for link in links:
        print "Retrieving data from %s ..."%(link)
        html = urlopen(link).read()
        soup = BeautifulSoup(html, 'lxml')
        climate_table = soup.find('table', 'TablaClima')
        
        if not climate_table is None:
            title = link.split("/")[-2]
            climate_rows = climate_table.findAll('tr')
            for row in climate_rows[1:]:
                data = row.findAll('td')
                print_line = [title]
                for datum in data:
                    a = ','.join(datum.findAll(text=True))
                    print_line.append(a)
                csv_writer.writerow(print_line)

if __name__ == '__main__':
    main()
