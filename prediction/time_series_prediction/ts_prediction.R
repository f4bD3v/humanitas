#############################################################
#############################################################

## This script is for time series prediction using regression 
## model with ARMA error shock in a rolling fashion

#############################################################
#############################################################

#please manually set the work space to your local directory
setwd("~/work/R/india")

#############################################################
#############################################################


rm(list=ls())
source('functions.R')
library(hydroGOF)
library(rugarch)
library(forecast)
library(PerformanceAnalytics)
library(QRM)
 
name = c()
name[1] = "wholesale-daily-('Gujarat', 'Vadhvan', 'Potato', 'Potato', 0.83).csv"
name[2] = "wholesale-daily-('NCT of Delhi', 'Najafgarh', 'Wheat', 'Dara', 0.82).csv"
name[3] = "wholesale-daily-('Uttar Pradesh', 'Bareilly', 'Apple', 'Delicious', 0.9).csv"
name[4] = "wholesale-daily-('Uttar Pradesh', 'Bareilly', 'Onion', 'Red', 0.91).csv"
name[5] = "wholesale-daily-('Uttar Pradesh', 'Bareilly', 'Rice', 'Coarse', 0.83).csv"
name[6] = "wholesale-daily-('West Bengal', 'Burdwan', 'Potato', 'Jyoti', 0.89).csv"
name[7] = "wholesale-daily-('West Bengal', 'Champadanga', 'Potato', 'Jyoti', 0.85).csv"
name[8] = "wholesale-daily-('West Bengal', 'Champadanga', 'Rice', 'Ratnachudi (718 5-749)', 0.94).csv"
  
folder.seq = "sequential/"
folder.4days = "4days/"

path.4days = c()
path.seq = c()
write.sum.cor = FALSE


for (i in 1:8){
  path.4days[i] = paste(folder.4days, name[i], sep='')
  path.seq[i] = paste(folder.seq, name[i], sep='')
  if (write.sum.cor){
    data.4days = as.matrix(read.table(path.4days[i], header=TRUE, sep=','))
    data.seq = as.matrix(read.table(path.seq[i], header=TRUE, sep=','))
    summary.table.4days = summary(data.4days)
    summary.table.seq = summary(data.seq)
    cor.table.4days = cor(data.4days)
    cor.table.seq = cor(data.seq)
    write.csv(x=summary.table.4days, file=paste('summary/4days ', name[i], sep=''))
    write.csv(x=summary.table.seq, file=paste('summary/seq ',name[i], sep=''))
    write.csv(x=cor.table.4days, file=paste('cor/4days ',name[i], sep=''))
    write.csv(x=cor.table.seq, file=paste('cor/seq ', name[i], sep=''))
  }
}



#path.price = "india_original_wholesale_daily_interpolated_0.4.csv"

#retail = as.matrix(read.table(path1, header = TRUE, sep = ","))
WestBengal.Potato = TRUE
if(WestBengal.Potato){
  data = as.matrix(read.table(path.seq[6], header=TRUE, sep=','))

  data = data[,-1]
  data = data[,-3]
  data.simple = data
  c.names = colnames(data)
  #data = data[,-3]
  price.idx = 3
  
  #lag quarters, 1 quarter~20 quarters(5 years)
  for(i in 1:8){
    lag = round(i*365/4)
    data = cbind(data, lagger(data[,price.idx], lag))
    c.names = c(c.names, paste('price_',lag, sep=''))
  }
  N = dim(data)[1]
  data.trunc = data[(lag+1):N,]
  colnames(data.trunc) = c.names
  #lag 1~5 years
#   for(i in 1:5){
#     lag = i*365
#     data = cbind(data, lagger(data[,1], lag))
#     c.names = c(c.names, paste('oil_',lag, sep=''))
#   }
#   
#   #lag months, 1~6 months
#   for(i in 1:6){
#     lag = i*30
#     data = cbind(data, lagger(data[,2], lag))
#     c.names = c(c.names, paste('inflation_',lag, sep=''))
#   }
  colnames(data) = c.names
  label = path.seq[6]
}else{
  data = as.matrix(read.table(path.seq[1], header=TRUE, sep=','))
  data = data[,-7]
  data = data[,-1]
  data = data[,-3]
  price.idx = 5
  label = path.seq[1]
}


N = dim(data)[1]
summary(data)
View(cor(data, use='complete.obs'))

ret = qrm.price2ret(data, ret.type='simple')

data.ts = ts(data, start = c(2005,1,1), end=c(2014,3,31), frequency=365)
ret.ts = ts(ret, start = c(2005,1,1), end=c(2014,3,31), frequency=365)*100

plot.ts(data.ts[,price.idx])
plot(ret.ts[,price.idx], main='first difference in percentage')

for(tkr in colnames(ret.ts)){
  acf(ret.ts[,tkr], lag.max=365*5, main=tkr, xlab='lag in years', na.action=na.pass)
}

seasonal = stl(data.ts[,price.idx], s.window="periodic")
plot(seasonal, main='Seasonal Decomposition of Price of Potato in West Bengal')


#################################################################################
#################################################################################
#################################################################################
#data.trunc 2588*11
###########3 years
fc.step = 7
win.size = 365*3#2588 - fc.step
arima.reg.7.3 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

#data.trunc 2588*11
fc.step = 30
win.size = 365*3#2588 - fc.step
arima.reg.30.3 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

###########5 years
fc.step = 7
win.size = 365*5#2588 - fc.step
arima.reg.7.5 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

#data.trunc 2588*11
fc.step = 30
win.size = 365*5#2588 - fc.step
arima.reg.30.5 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

###########7 years
fc.step = 7
win.size = 365*7#2588 - fc.step
arima.reg.7.7 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

#data.trunc 2588*11
fc.step = 30
win.size = 365*7#2588 - fc.step
arima.reg.30.7 = moving.window.prediction(data.trunc[,price.idx], reg=data.trunc[,-price.idx], win.size=win.size, fc.step=fc.step)

#################################################################################
#################################################################################


arima.reg.profile.7.3 = get.pred.profile(data.trunc[,price.idx], arima.reg.7.3, win.size+1)
arima.reg.profile.30.3 = get.pred.profile(data.trunc[,price.idx], arima.reg.30.3, win.size+1)

arima.reg.profile.7.5 = get.pred.profile(data.trunc[,price.idx], arima.reg.7.5, win.size+1)
arima.reg.profile.30.5 = get.pred.profile(data.trunc[,price.idx], arima.reg.30.5, win.size+1)

arima.reg.profile.7.7 = get.pred.profile(data.trunc[,price.idx], arima.reg.7.7, win.size+1)
arima.reg.profile.30.7 = get.pred.profile(data.trunc[,price.idx], arima.reg.30.7, win.size+1)



#################################################################################
#####################################################################################

plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.3, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.3, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)

plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.3, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.3, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)


plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.5, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.5, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)

plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.5, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.5, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)

plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.7, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.7.7, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)

plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.7, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'))
plot.pred(stack=FALSE, data.trunc[,price.idx], arima.reg.30.7, main=paste('Regression with moving window size ',win.size/365,'yr, forecast step', fc.step,'days'), start.idx=2000)



#################################################################################
#####################################################################################
######################################################################################
