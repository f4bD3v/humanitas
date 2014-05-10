from bs4 import BeautifulSoup
from urllib2 import urlopen
import csv

BASE_URL = 'http://www.tutiempo.net'
PAGE_1 = '/en/Climate/India/IN.html'
PAGE_2 = '/en/Climate/India/IN_2.html'
headings = ['Location', 'Year', 'Month', 'T', 'TM', 'Tm', 'SLP', 'H', 'PP', 'VV', 'V', 'VM', 'VG', 'RA', 'SN', 'TS', 'FG']

MAX_ROWS = 100000
FIRST_YEAR = 1999

def get_links(url):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'lxml')
    location_links = soup.find('div', id='ListadosV4')
    locations_links = [BASE_URL + li.a['href'] for li in location_links.findAll('li')]
    return locations_links

def write_log(message):
    f_log = open("log.txt", 'a')
    f_log.write(message)
    f_log.close()

def main():
    links = get_links(BASE_URL + PAGE_1)
    links.extend(get_links(BASE_URL + PAGE_2))
        
    csvfile = open('climate_data_1.csv', 'wb')
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(headings)

    num_rows = 0; num_files = 1
    
    for link in links:
        print ('Retrieving data from %s ...\n'%(link))
        html = urlopen(link).read()
        soup = BeautifulSoup(html, 'lxml')
        year_list = soup.find('div', id='SelectYear')
        title = link.split('/')[-2]
        print ('Location: %s\n'%(title))
        if year_list is None:
            continue

        for li in year_list.findAll('li'):
            year = int(','.join(li.findAll(text=True)))
            print (str(year) + '\n')
            if year >= FIRST_YEAR:
                html = urlopen(BASE_URL + li.a['href']).read()
                soup = BeautifulSoup(html, 'lxml')
                month_list = soup.find('div', id='SelectMes')
                if month_list is None:
                    month_list = soup.find('div','ListasLeft')
                    if month_list is None:
                        continue
                    
                for month in month_list.findAll('li'):
                    month_name = ','.join(month.findAll(text=True))
                    if month_name[0:10] == 'Historical':
                        month_name = month_name.split(" ")[1]
                    print (month_name + '\n')
                    html = urlopen(BASE_URL + month.a['href']).read()
                    soup = BeautifulSoup(html, 'lxml')
                    climate_table = soup.find('table', 'TablaClima')
                    
                    if climate_table is None:
                        continue
                    climate_rows = climate_table.findAll('tr')
                    
                    for row in climate_rows[1:-2]:
                        data = row.findAll('td')
                        print_line = [title, year, month_name]
                        for datum in data:
                            a = ','.join(datum.findAll(text=True))
                            print_line.append(a.encode('utf8'))
                        csv_writer.writerow(print_line)
                        num_rows += 1
                        if num_rows == MAX_ROWS:
                            csvfile.close()
                            num_files += 1
                            csvfile = open('climate_data_%s.csv'%(num_files), 'wb')
                            csv_writer = csv.writer(csvfile)
                            csv_writer.writerow(headings)
                            num_rows = 0
    csvfile.close()

if __name__ == '__main__':
    main()
