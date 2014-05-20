#############################################################
#############################################################

## This script is for time series analysis of stationarity,
## autocorrelations, and seasonal patterns

#############################################################
#############################################################

#please manually set the work space to your local directory
setwd("~/work/R/india")

#############################################################
#############################################################


source('functions.R')

name.inf = "inflation_for_discount.csv"
name.good = "good_series_wholesale_daily.csv"
good.series = as.matrix(read.table(name.good, header=TRUE, row.names=1, sep=','))
price = good.series[,'X..West.Bengal....Burdwan....Potato....Jyoti...0.89.']
inf = as.matrix(read.table(name.inf, header=TRUE, row.names = 1, sep=','))
price.disc = price/inf

price.ts = ts(price, start = c(2005,1,1), end=c(2014,3,31), frequency=365)
price.disc.ts = ts(price.disc, start = c(2005,1,1), end=c(2014,3,31), frequency=365)
ret.ts = ts(diff(price), start = c(2005,1,1), end=c(2014,3,31), frequency=365)#= ts(qrm.price2ret(price, ret.type='simple'), start = c(2005,1,1), end=c(2014,3,31), frequency=365)
ret.disc.ts = ts(diff(price.disc), start = c(2005,1,1), end=c(2014,3,31), frequency=365)#= ts(qrm.price2ret(price.disc, ret.type='simple'), start = c(2005,1,1), end=c(2014,3,31), frequency=365)

seasonal.price = stl(price.ts, s.window='periodic')
seasonal.price.disc = stl(price.disc.ts, s.window='periodic')
seasonal.ret = stl(ret.ts, s.window='periodic')
seasonal.ret.disc = stl(ret.disc.ts, s.window='periodic')

plot(seasonal.price, main='Price of West Bengal Potato')
plot(seasonal.price.disc, main='Discounted Price of West Bengal Potato')
plot(seasonal.ret, main="Daily Difference of West Bengal Potato")
plot(seasonal.ret.disc, main="Discounted Daily Difference of West Bengal Potato")



summary(price.ts)
summary(price.disc.ts)
summary(ret.ts)
summary(ret.disc.ts)


acf(price.ts, lag.max=365*5, xlab='Lag in years')
acf(price.disc.ts, lag.max=365*5, xlab='Lag in years')
acf(ret.ts, lag.max=365*5, xlab='Lag in years')
acf(ret.disc.ts, lag.max=365*5, xlab='Lag in years', main='Correlogram of First Difference of Sample Series')

hist(ret.ts, breaks=100, freq=FALSE)
hist(ret.disc.ts, breaks=100, freq=FALSE)

x = ret.disc.ts
h<-hist(x, breaks=100)
xfit<-seq(min(x),max(x),length=100) 
yfit<-dnorm(xfit,mean=mean(x),sd=sd(x)) 
yfit <- yfit*diff(h$mids[1:2])*length(x) 
lines(xfit, yfit, col="blue", lwd=2)

library(QRM)
st.fit = fit.st(x)


library(tseries)
kpss.test(price.ts, null='Trend')
kpss.test(price.disc.ts, null='Trend')
kpss.test(diff(price.ts), null='Trend')
kpss.test(ret.ts, null='Trend')
kpss.test(ret.disc.ts, null='Trend')
