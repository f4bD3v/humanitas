qrm.price2ret <- function(prices, ret.type = "log", freq = NULL){ ## Converts prices into returns or log-returns
  if (!is.element(ret.type, c("log", "simple"))) { stop("Invalid 'ret.type' argument!")
  }
  ## Extract lower frequency prices if needed
  if (!is.null(freq)) {
    prices <- qrm.subsample(prices = prices, freq = freq)
  }
  ## Compte returns
  if (ret.type == "simple") {
    ret <- tail(prices, -1) / head(prices, -1) - 1
  } else {
    ret <- diff(log(prices))
  }
  ret
}


lagger = function(data, lag){
  ret = data
  for(i in 1:length(ret)){
    idx = i - lag
    if(idx <= 0){
      ret[i] = data[1]#NA
    }else{
      ret[i] = data[idx] 
    }
  }
  ret
}

moving.window.prediction = function(data, fit.fn=auto.arima, forecast.fn=forecast, reg=NULL, win.size, fc.step){
  arima.fc.win  = c()
  arima.higher.win = c()
  arima.lower.win = c()
  arima.fc.win[win.size] = NA
  arima.higher.win[win.size] = NA
  arima.lower.win[win.size] = NA
  reg.roll.win = NULL
  reg.roll.win.test = NULL
  N = length(data)
  i=1
  while(TRUE){
    #   print(N-out.sample+i-1)
    start.idx = i
    end.idx = i+win.size-1
    fc.start.idx = end.idx+1
    fc.end.idx = end.idx+fc.step
    if(fc.end.idx > N){
      break
    }
    
    train.roll.win = data[start.idx:end.idx]
    if(is.null(reg)){
      arima.fit.win = fit.fn(train.roll.win)
      fc.win = forecast.fn(arima.fit.win, h=fc.step)
    }else{
      reg.roll.win = reg[start.idx:end.idx, ]  
      reg.roll.win.test = reg[fc.start.idx:fc.end.idx,]
      arima.fit.win = fit.fn(train.roll.win, xreg = reg.roll.win)
      fc.win = forecast.fn(arima.fit.win, h=fc.step, xreg = reg.roll.win.test) 
    }
    
    print(paste(i,': train[', start.idx,':', end.idx,'], forecast[', fc.start.idx,':', fc.end.idx,']', sep=''))
    print(arima.fit.win$coef)
    
    arima.fc.win = c(arima.fc.win, fc.win$mean)
    arima.lower.win = c(arima.lower.win, fc.win$lower[,2])  #95% confidence interval
    arima.higher.win = c(arima.higher.win, fc.win$upper[,2])
    #     paste(arima.fc.win[predict.pos], arima.lower.win[predict.pos], arima.higher.win[predict.pos])
    i = i+fc.step
  }
  
  error = head(data, length(arima.fc.win)) - arima.fc.win
  
  list(fc = arima.fc.win,
       higher = arima.higher.win,
       lower = arima.lower.win,
       error = error)  
}

get.pred.profile = function(data, fc, start.idx, end.idx=NULL){
  pred = fc$fc
  lower = fc$lower
  higher = fc$higher
  if(is.null(end.idx)){
    end.idx = min(length(data), length(pred))
  }
  print(paste('start.idx: ', start.idx, ' end.idx: ', end.idx, sep=''))
  
  violations = count.violations(data, higher, lower, start.idx, end.idx)
  require(hydroGOF)
  MSE = mse(data[start.idx:end.idx], pred[start.idx:end.idx])
  RMSE = rmse(data[start.idx:end.idx], pred[start.idx:end.idx])
  ret = c(MSE=MSE, RMSE=RMSE, violations.count=violations$vio.count, violations.prob = violations$vio.prob)
  print(ret)
  ret
}

count.violations = function(data, higher, lower, start.idx, end.idx = NULL){
  if(is.null(end.idx)){
    end.idx = min(length(data), length(higher))
  }
  
  vio.count = c()
  for(idx in start.idx:end.idx){
    if(data[idx] > higher[idx] || data[idx] < lower[idx]){
      vio.count[idx] = 1
    }
    else{
      vio.count[idx] = 0
    }
  }
  
  ret = list(#vio.vec = vio.count, 
       vio.count = sum(vio.count, na.rm=TRUE),
       vio.prob = sum(vio.count, na.rm=TRUE)/(end.idx - start.idx + 1))  
  ret
}

plot.pred = function(data, fc, main, start.idx=NULL, stack=TRUE){
  if(is.null(start.idx)){
    start.idx=1
  }
  data = data[start.idx:length(data)]
  pred = fc$fc[start.idx:length(fc$fc)]
  lower = fc$lower[start.idx:length(fc$lower)]
  higher = fc$higher[start.idx:length(fc$higher)]
  error = fc$error[start.idx:length(fc$error)]
  if(stack){
    par(mfrow=c(3,1))
  }
  else{
    par(mfrow=c(1,1))
  }
  plot(data, type='l', col='blue', main=main, ylim=c(0, max(data, na.rm=TRUE)), xlab='day count', ylab='price')
  lines(pred, col='red')
  legend("topleft", legend=c('actual', 'predict'), col=c('blue', 'red'), lty=c(1,1))
#   lines(lower, col='orange')
#   lines(higher, col='orange')
#   legend("topleft", legend=c('actual', 'predict', '95% conf.interval'), col=c('blue', 'red', 'orange'), lty=c(1,1,1))
  
#   plot(higher-lower, type='l', ylim = c(0,max(data, na.rm=TRUE)), col='purple')
#   lines(abs(error), col='gray')
#   legend('topleft', legend=c('range of confidence interval', '|prediction error|'), col=c('purple', 'gray'), lty=c(1,1))
#   
  hist.qq(error, main='Histogram of Prediction Errors')
#   hist.qq.99(error, main='Histogram of Prediction Errors')
}

hist.qq = function(data, breaks=100, main){
  q1 = round(quantile(data, 0.95, na.rm=TRUE), digits=2)
  q2 = round(quantile(data, 0.05, na.rm=TRUE), digits=2)
  txt1 = paste('95% quantile (', q2, ',', q1, ')', sep='')
  
  q3 = round(quantile(data, 0.99, na.rm=TRUE), digits=2)
  q4 = round(quantile(data, 0.01, na.rm=TRUE), digits=2)
  txt2 = paste('99% quantile (', q4, ',', q3, ')')
  
  hist(data, breaks=breaks, freq=TRUE, main=main)
  abline(v=q1, col='red')
  abline(v=q2, col='red')
  abline(v=q3, col='orange')
  abline(v=q4, col='orange')
  legend("topleft", legend=c(txt1, txt2), col=c('red', 'orange'), lty=c(1,1))
}

hist.qq.99 = function(data, breaks=100, main){
  q1 = round(quantile(data, 0.99, na.rm=TRUE), digits=2)
  q2 = round(quantile(data, 0.01, na.rm=TRUE), digits=2)
  txt = paste('99% quantile [', q2, ',', q1, ']')
  hist(data, breaks=breaks, freq=TRUE, main=main)
  abline(v=q1, col='red')
  abline(v=q2, col='red')
  legend("topleft", legend=txt, col='red', lty=1)
}
