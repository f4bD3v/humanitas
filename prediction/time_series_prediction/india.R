rm(list=ls())
setwd("~/work/R/india")
source('functions.R')
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
data = as.matrix(read.table(path.seq[1], header=TRUE, sep=','))
data = data[,-7]
data = data[,-1]
data = data[,-3]
summary(data)
cor(data)
ret = qrm.price2ret(data, ret.type='simple')
recover = qrm.ret2price(as.matrix(ret[,5]), ret.type='simple', start.val = data[1,5])
data.ts = ts(data, start = c(2005,1,1), end=c(2014,3,31), frequency=365)
ret.ts = ts(ret, start = c(2005,1,1), end=c(2014,3,31), frequency=365)
plot(data.ts)
plot(ret.ts)
for(tkr in colnames(ret.ts)){
  acf(ret.ts[,tkr], lag.max=365*5, main=tkr)
}

#training set and testing set
out.sample = 600
N = dim(data)[1]
train = head(data, N-out.sample)
test = tail(data, out.sample)
#train = head(ret, N-out.sample)
#test= tail(ret, out.sample)
train.df = data.frame(price = train[,5], temp=train[,1], PP=train[,2], oil=train[,3], inflation=train[,4])
test.df = data.frame(price = test[,5], temp=test[,1], PP=test[,2], oil=test[,3], inflation=test[,4])


#simple linear regression
lm.fit = lm(price ~ temp+PP+oil+inflation, data = train.df)
lm.fit
lm.fc = c()
mse = c()
for(i in 1:out.sample){
  lm.fc[i] = sum(c(1, test[i,1:4])*lm.fit$coefficients)
  mse[i] = (test[i] - lm.fc[i])^2
}
plot(mse, type='l', main="MSE")
sum(mse)/out.sample

plot(1:N, c(train.df$price,test.df$price), col='blue', type="l", ylim=c(0, max(test.df$price)), main='linear reg training and test')
lines(lm.fit$fitted.values, col='green')
lines((N-out.sample+1):N, lm.fc, col='red')
legend("topleft", legend=c('actual', 'fitted', 'predicted'), col=c('blue', 'green', 'red'), lty=c(1,1,1))

#ARMA 
arima.fit = auto.arima(diff(train.df$price))
arima.fit
#plot(forecast(arima.fit, h=100))
#acf(residuals(arima.fit), lag.max = 100)
#Box.test(residuals(arima.fit), lag=100)
#plot(forecast(arima.fit, h=1000))

#rolling ARMA, refit ARMA for longer and longer training sets
arima.fc  = c()
arima.higher = c()
arima.lower = c()
out.sample = 50
for(i in 1:out.sample){
  print(N-out.sample+i-1)
  train.roll = head(data, N-out.sample+i-1)
  arima.fit = auto.arima(diff(train.roll[,5]))
  print(i)
  print(arima.fit$coef)
  fc = forecast(arima.fit, h=1)
  arima.fc[i] = fc$mean[1]
  arima.lower[i] = fc$lower[2]  #95% confidence interval
  arima.higher[i] = fc$upper[2]
}

arima.fc.price = cumsum(c(train.roll[N-out.sample,5],arima.fc))
arima.lower.price = cumsum(c(train.roll[N-out.sample,5],arima.lower))
arima.higher.price = cumsum(c(train.roll[N-out.sample,5],arima.higher))
plot(arima.fc.price, ylim=c(min(arima.lower.price), max(arima.higher.price)), type='l')
lines(arima.lower.price, col='orange')
lines(arima.higher.price, col='orange')
lines(tail(data[,5], out.sample), col='blue')

#on-time fitted ARMA
arima.fit1 = auto.arima(diff(train.df$price), max.p=10, max.d=0, max.q=10)
arima.fit1
a1 = arima.fit1$coef[1]
m1 = arima.fit1$coef[2]
for(i in 1:out.sample){
  
}


#regression with ARMA shock
arima.reg = auto.arima(diff(train.df$price),xreg=diff(train.df[,2:5]))
arima.reg
plot(forecast(arima.reg, xreg=test.df[2:5]))
lines(data[,5])



library(rugarch)
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




library(forecast)
seasonal = stl(data.ts[,1], s.window="periodic")
plot(seasonal)

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
