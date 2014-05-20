# rm(list=ls())
setwd("~/work/R/india")
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


#training set and testing set
out.sample = 600
train = head(data, N-out.sample)
test = tail(data, out.sample)
#train = head(ret, N-out.sample)
#test= tail(ret, out.sample)
# if(WestBengal.Potato){
#   train.df = data.frame(price = train[,price.idx], oil=train[,1], inflation=train[,2])
#   test.df = data.frame(price = test[,price.idx], oil=test[,1], inflation=test[,2])
# }else{
#   train.df = data.frame(price = train[,price.idx], temp=train[,1], PP=train[,2], oil=train[,3], inflation=train[,4])
#   test.df = data.frame(price = test[,price.idx], temp=test[,1], PP=test[,2], oil=test[,3], inflation=test[,4])  
# }
# 
# 
# #simple linear regression
# if(WestBengal.Potato){
#   lm.fit = lm(price ~ oil+inflation, data = train.df)
# }else{
#   lm.fit = lm(price ~ temp+PP+oil+inflation, data = train.df)  
# }
# 
# lm.fit
# lm.fc = c()
# mse = c()
# for(i in 1:out.sample){
#   if(WestBengal.Potato){
#     lm.fc[i] = sum(c(1, test[i,1:2])*lm.fit$coefficients)
#   }else{
#     lm.fc[i] = sum(c(1, test[i,1:4])*lm.fit$coefficients)  
#   }
#   
#   mse[i] = (test[i] - lm.fc[i])^2
# }
# plot(mse, type='l', main="MSE")
# sum(mse)/out.sample
# 
# plot(1:N, c(train.df$price,test.df$price), col='blue', type="l",  main='linear reg training and test')
# lines(lm.fit$fitted.values, col='green')
# lines((N-out.sample+1):N, lm.fc, col='red')
# legend("topleft", legend=c('actual', 'fitted', 'predicted'), col=c('blue', 'green', 'red'), lty=c(1,1,1))

#ARMA 
# arima.fit = auto.arima(diff(train.df$price))
# arima.fit
#plot(forecast(arima.fit, h=100))
#acf(residuals(arima.fit), lag.max = 100)
#Box.test(residuals(arima.fit), lag=100)
#plot(forecast(arima.fit, h=1000))

#rolling ARMA, refit ARMA for longer and longer training sets
# arima.fc  = c()
# arima.higher = c()
# arima.lower = c()
# out.sample = 600
# fc.step = 1
# for(i in 1:out.sample){
#   print(i)
#   train.roll = head(data, N-out.sample+i-1)
#   arima.fit = auto.arima(train.roll[,price.idx])
#   print(arima.fit$coef)
#   fc = forecast(arima.fit, h=fc.step)
#   predict.pos = N-out.sample+i-1+fc.step
#   arima.fc[predict.pos] = fc$mean[1]
#   arima.lower[predict.pos] = fc$lower[2]  #95% confidence interval
#   arima.higher[predict.pos] = fc$upper[2]
#   paste(arima.fc[predict.pos], arima.lower[predict.pos], arima.higher[predict.pos])
# }

# plot.pred(data[,price.idx], arima.fc, arima.higher, arima.lower, main='ARMA longer and longer training set')
# plot.pred(data[(N-out.sample+1):N,price.idx], arima.fc[(N-out.sample+1):N], arima.higher[(N-out.sample+1):N], arima.lower[(N-out.sample+1):N], main='ARMA longer and longer training set zoom')

#arima.profile = get.pred.profile(data[,price.idx], arima.higher, arima.lower, N-out.sample+1)


#rolling ARMA, refit ARMA for fixed moving window of training data
win.size = 600
arima.forecast.win = moving.window.prediction(data[,price.idx], win.size=win.size, fc.step=1)
arima.profile.win = get.pred.profile(data[,price.idx], arima.forecast.win, win.size+1)
svg('1.svg', width=18, height=7)
plot.pred(data[,price.idx], arima.forecast.win, main='ARMA moving window(600), fc.step==1')
dev.off()

arima.forecast.win.7 = moving.window.prediction(data[,price.idx], win.size=win.size, fc.step=7)
arima.profile.win.7 = get.pred.profile(data[,price.idx], arima.forecast.win.7, win.size+1)
svg('2.svg', width=18, height=7)
plot.pred(data[,price.idx], arima.forecast.win.7, main='ARMA moving window(600), fc.step==7')
dev.off()
plot.pred(data[,price.idx], arima.forecast.win.7, main='ARMA moving window(600), fc.step==7', start.idx=N-200)

arima.forecast.win.30 = moving.window.prediction(data[,price.idx], win.size=win.size, fc.step=30)
arima.profile.win.30 = get.pred.profile(data[,price.idx],  arima.forecast.win.30, win.size+1)
svg('3.svg', width=18, height=7)
plot.pred(data[,price.idx], arima.forecast.win.30, main='ARMA moving window(600), fc.step==30')
dev.off()





# plot(data[(N-out.sample+1):N,price.idx], type='l', col='blue', main='ARMA moving window')
# lines(arima.fc.win[(N-out.sample+1):N], col='green')
# lines(arima.lower.win[(N-out.sample+1):N], col='orange')
# lines(arima.higher[(N-out.sample+1):N], col='orange')
# legend("topleft", legend=c('actual', 'predict', '95% conf.interval'), col=c('blue', 'green', 'orange'), lty=c(1,1,1))

# i=50
# train.roll = head(data, N-out.sample+i-1)
# arima.fit = auto.arima(train.roll[,price.idx])
# fc = forecast(arima.fit, h=100)
# plot(fc)
# i=600
# train.roll = head(data, N-out.sample+i-1)
# arima.fit = auto.arima(train.roll[,price.idx])
# fc = forecast(arima.fit, h=1)
# plot(fc)

# 
# arima.fc.price = cumsum(c(train.roll[N-out.sample,price.idx],arima.fc))
# arima.lower.price = cumsum(c(train.roll[N-out.sample,price.idx],arima.lower))
# arima.higher.price = cumsum(c(train.roll[N-out.sample,price.idx],arima.higher))
# plot(arima.fc.price, ylim=c(min(arima.lower.price), max(arima.higher.price)), type='l')
# lines(arima.lower.price, col='orange')
# lines(arima.higher.price, col='orange')
# lines(tail(data[,price.idx], out.sample), col='blue')


#regression with ARMA shock
win.size=600
arima.reg = moving.window.prediction(data[,price.idx], reg=data[,-price.idx], win.size=win.size, fc.step=7)
arima.reg.profile = get.pred.profile(data[,price.idx], arima.reg, win.size+1)
plot.pred(stack=FALSE, data[,price.idx], arima.reg, main='Regression with moving window(600), fc.step==7')
plot.pred(stack=FALSE, data[,price.idx], arima.reg, main='ARMA regression moving window(600), fc.step==7', start.idx=N-300)

#data.simple 
fc.step = 7
win.size = 1000
arima.reg.1000 = moving.window.prediction(data.simple[,price.idx], reg=data.simple[,-price.idx], win.size=win.size, fc.step=fc.step)
arima.reg.profile.1000 = get.pred.profile(data.simple[,price.idx], arima.reg.1000, win.size+1)
plot.pred(stack=FALSE, data.simple[,price.idx], arima.reg.1000, main=paste('Regression with moving window size ',win.size,', forecast step ', fc.step))
plot.pred(stack=FALSE, data[,price.idx], arima.reg.1000, main=paste('Regression with moving window size ',win.size,', forecast step ', fc.step), start.idx=3000)

#data
fc.step = 7
win.size = 1000
arima.reg.1000 = moving.window.prediction(data[,price.idx], reg=data[,-price.idx], win.size=win.size, fc.step=fc.step)
arima.reg.profile.1000 = get.pred.profile(data[,price.idx], arima.reg.1000, win.size+1)
plot.pred(stack=FALSE, data[,price.idx], arima.reg.1000, main=paste('Regression with moving window size ',win.size,', forecast step ', fc.step))
plot.pred(stack=FALSE, data[,price.idx], arima.reg.1000, main=paste('Regression with moving window size ',win.size,', forecast step ', fc.step), start.idx=3000)

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

fc.step = 60
win.size = N-fc.step
arima.reg.3000 = moving.window.prediction(data[,price.idx], reg=data[,-price.idx], win.size=win.size, fc.step=fc.step)
arima.reg.profile.3000 = get.pred.profile(data[,price.idx], arima.reg.3000, win.size+1)
plot.pred(stack=FALSE, data[,price.idx], arima.reg.3000, main=paste('ARMA regression moving window',win.size,'fc.step', fc.step))
plot.pred(stack=FALSE, data[,price.idx], arima.reg.3000, main=paste('ARMA regression moving window',win.size,'fc.step', fc.step), start.idx=3000)

########################################################
####     ARMA GARCH    #################################
########################################################

model=ugarchspec(
  variance.model = list(model = "sGARCH", garchOrder = c(1,1)),
  mean.model = list(armaOrder = c(1,1), include.mean = TRUE),
  distribution.model = 'std'
)

modelfit.ret = ugarchfit(spec=model,data=ret.1, out.sample=out.sample)
#plot(modelfit.ret)
modelfc.ret = ugarchforecast(modelfit.ret, n.ahead = 7, n.roll = out.sample)
#plot(modelfc.ret)
#modelfit.logret = ugarchfit(spec=model,data=logret.1, out.sample=1000)
#modelfc.logret = ugarchforecast(modelfit.logret, n.ahead = 10, n.roll = 0)

recover.1 = qrm.ret2price(as.matrix(fitted(modelfit.ret)), ret.type = "simple", start.val = data[1,1])


model=ugarchspec(
  variance.model = list(model = "sGARCH", garchOrder = c(1,1)),
  mean.model = list(armaOrder = c(1,1), include.mean = TRUE),
  distribution.model = 'std'
)

modelfit.data = ugarchfit(spec=model, data=data[,1], out.sample = out.sample)
modelfc.data = ugarchforecast(modelfit.data, n.ahead = 7, n.roll=out.sample)

arfima.data = autoarfima(data=data[,1])






seasonal.ret.1 = stl(ret.1, s.window='periodic')

len = dim(data.ts)[1]
arima.fit = auto.arima(data.ts[1:(len-60),1])
accuracy(arima.fit)
arima.fc = forecast(arima.fit, h=60)
plot(arima.fc$x)
plot(arima.fc$fitted)
plot(arima.fc$residuals)

fitted = data.ts[,1] - arima.fit$residuals

plot(data.ts[,1], col='blue')
lines(fitted, col='red')
