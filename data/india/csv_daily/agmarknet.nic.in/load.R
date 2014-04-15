d=as.data.frame(read.csv('india_Rice_daily_2005-2014.csv', header=FALSE))
names(d) = list('date', 'freq', 'country', 'region', 'product', 'subproduct',
             'price')
d$date = as.Date(d$date, format='%d/%m/%Y')
d$year = as.numeric(format(d$date, '%Y'))
d$day = as.numeric(format(d$date, '%j'))
d$week = as.numeric(format(d$date, '%V'))
d = d[order(d$day),] # sort by day nb
d$price = as.numeric(d$price)
attach(d)
