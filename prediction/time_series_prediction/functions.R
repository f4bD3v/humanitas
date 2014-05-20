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
  hist.qq.99(error, main='Histogram of Prediction Errors')
}

hist.qq = function(data, breaks=100, main){
  q1 = round(quantile(data, 0.95, na.rm=TRUE), digits=2)
  q2 = round(quantile(data, 0.05, na.rm=TRUE), digits=2)
  txt = paste('95% quantile [', q2, ',', q1, ']')
  hist(data, breaks=breaks, freq=TRUE, main=main)
  abline(v=q1, col='red')
  abline(v=q2, col='red')
  legend("topleft", legend=txt, col='red', lty=1)
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


getAdjusted = function(tickers){
  ret = c()
  i=1
  for(tkr in tickers){
    if(grepl('Adjusted', tkr)){
      ret[i] = tkr
      i = i+1
    }
  }
  ret
}
qrm.ret2price <- function(ret, ret.type = "simple", start.val = 100, start.date = NULL){ ## Converts simple returns or log-returns into prices
  ##
  ## Arguments:
  ##
  ##
  ##
  ##
  ##
  ##
  ## Value:
  ##   A matrix with the prices.
  ##---------------------------------------------------------------------------------
  ## Validate input
  if (!is.element(ret.type, c("log", "simple"))) { stop("Invalid 'ret.type' argument!")
  }
  ## Convert log-returns to simple returns (if needed)
  if (ret.type == "log") { ret <- exp(ret) - 1
  }
  ## Compte prices with starting value of 1
  prices <- cbind(1, apply(1 + ret, 2, cumprod))
  ## Rebase prices
  prices <- prices * matrix(start.val, nrow = nrow(prices), ncol = ncol(prices)) 
  ## Add start date to matrix' row names
  if (!is.null(start.date)) {
    rownames(prices)[1] <- start.date }
  prices[,2]
}

qrm.load.data <- function(file.path, sep = ";") {
  if(sep ==";"){
    as.matrix(read.table(file.path, header = TRUE, row.names = 1, sep = sep))
  }
  else if(sep=="TAB"){
    as.matrix(read.delim(file.path, header = TRUE, row.names=1))
  }
}

library(forecast)

get.security <- function(equity, ticker){
  equity[, which(colnames(equity)==ticker)]
}

qrm.clean.prices <- function(prices, method = "last") {
  nas <- is.na(prices)
  first.val <- apply(!nas, 2, which.max)
  nb.na     <- apply(nas, 2, sum)
  nb.na     <- nb.na - first.val + 1
  na.prop   <- nb.na / (nrow(prices) - first.val + 1)
  ## Get longest run of NAs for each security
  max.na.run <- rep(NA, ncol(prices)) 
  for (j in 1:ncol(prices)) {
    if (nb.na[j] == 0) { max.na.run[j] <- 0
    } else {
      vec <- as.vector(head(prices[, j], -first.val[j])) 
      rles <- rle(is.na(vec))
      max.na.run[j] <- max(rles$lengths[rles$values])
    } }
  max.na.run
  
  if (method == "last") { 
    require(zoo)
    prices.clean <- apply(prices, 2, na.locf, na.rm = FALSE) } 
  else if (method == "remove") {
    prices.clean <- prices[!apply(nas, 1, any), ] } 
  else if(method == "zero"){
    prices.clean = prices
    prices.clean[is.na(prices.clean)] = 0
  }
  else {
    stop("Invalid 'method' argument!") }
  ## Function output
  list(prices.clean = prices.clean,
       nb.na        = nb.na,
       na.prop      = na.prop,
       max.na.run   = max.na.run)
}

qrm.subsample <- function(prices, start.date = NULL, end.date = NULL, tickers = NULL, freq = NULL){
  if (is.null(start.date)) {
    start.date <- rownames(prices)[1]
  }
  if (is.null(end.date)) {
    end.date <- tail(rownames(prices), 1) }
  if (is.null(tickers)) {
    tickers <- colnames(prices)
  }
  if (is.null(freq)) {
    freq <- "asis" }
  if (!is.element(freq, c("asis", "week", "month"))) { stop("Invalid 'freq' argument!")
  }
  dates     <- as.Date(rownames(prices))
  date.cond <- (dates >= as.Date(start.date)) & (dates <= as.Date(end.date))
  prices    <- prices[date.cond, tickers, drop = FALSE]
  if (is.element(freq, c("week", "month"))) {
    dates.all <- as.character(seq.Date(from = as.Date(start.date),
                                       to = as.Date(end.date), by = "day"))
    dates.freq <- as.character(seq.Date(from = as.Date(start.date),
                                        to = as.Date(end.date), by = freq))
    ind.avail  <- match(rownames(prices), dates.all)
    prices.all <- matrix(NA, nrow = length(dates.all), ncol = ncol(prices),
                         dimnames = list(dates.all, colnames(prices)))
    prices.all[ind.avail, ] <- prices
    prices.all <- qrm.clean.prices(prices.all)$prices.clean
    prices     <- prices.all[dates.freq, ]
  }
  
  prices
}

tkr.filter <- function(equity, all.tickers, start.date=NULL, end.date=NULL, threshold=150){
  good.tickers = c()
  counter = c()
  min = 1000000
  i=1
  for(tkr in all.tickers){
    this.stock <- qrm.subsample(equity, tickers=tkr, start.date, end.date)
    na.count = apply(this.stock, 2, function(x) length(which(is.na(x))))
    if(na.count <= threshold){
      good.tickers[i] = tkr
      counter[i] = na.count
      i = i+1
    }
    if(na.count < min){
      min = na.count
    }
  }
  good.tickers
}

na.count <- function(equity, start.date=NULL, end.date=NULL){
  na.counter = c()
  if(!is.null(start.date)){
    for(tkr in colnames(equity)){
      this.stock <- qrm.subsample(equity, tickers=tkr, start.date, end.date)
      na.counter[[tkr]] <- apply(this.stock, 2, function(x) length(which(is.na(x))))
    }
  }
  else{
    for(tkr in colnames(equity)){
      this = equity[,tkr]
      na.counter[[tkr]] = apply(equity[,tkr, drop=FALSE],2,function(x) length(which(is.na(x))))
    }
  }
  na.counter
}

na.maxlen  = function(equity, start.date=NULL, end.date=NULL){
  maxlen = c()
  if(!is.null(start.date)){
    maxlen = na.maxlen(qrm.subsample(equity, start.date=start.date))
  }
  else{
    for(tkr in colnames(equity)){
      this = equity[,tkr]
      count = 0
      longest = 0
      for(i in 1:length(this)){
        if(is.na(this[i])){
          count = count + 1
        }
        else{
          count = 0
        }
        if(count > longest){
          longest = count
        }
      }
      maxlen[[tkr]] = longest
    }
  }
  maxlen
}

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


draw.plots <- function(data, my.tickers=colnames(data), rows, cols, txt){
  par(mfrow=c(rows,cols), mar=c(3,3,5,1))
  for(tkr in my.tickers){
    plot(data[,tkr], type='l',main=paste(txt, "of", tkr))
  }
  
}


draw.acfs <- function(data, my.tickers=colnames(data), rows, cols, txt){
  par(mfrow=c(rows,cols), mar=c(1,4,5,1))
  for(tkr in my.tickers){
    acf(data[,tkr], type="correlation", plot=TRUE, na.action=na.pass, main=paste("ACF:", txt, "of", tkr))
  }
}


draw.ccfs <- function(data, my.tickers=colnames(data), rows, cols, txt){
  par(mfrow=c(rows,cols), mar=c(1,4,5,1))
  data = as.matrix(data)
  for(tkr in my.tickers){
    ts1 = ts(data[,tkr])
    ts2 = ts1^2
    ts1 = ts1[1:length(ts1)]
    ts2 = ts2[1:length(ts2)]
    ccf(ts1, ts2, lag.max = 500, type="correlation", plot=TRUE, na.action=na.pass, main=paste("CCF:", txt, "of", tkr))
  }
}

draw.hists <- function(data, my.tickers=colnames(data), rows, cols, brks=100, txt){
  par(mfrow=c(rows, cols), mar = c(3, 4.1, 2, 0.5))
  for(tkr in my.tickers){
    data = na.omit(data)
    hist(data[,tkr], xlim=range(data), breaks=brks, freq=FALSE, main=paste("Histogram:",txt, "of", tkr))
    x <- seq(min(data[, tkr]), max(data[, tkr]), length.out = 100)
    lines(x, dnorm(x, mean(data[, tkr]), sd(data[, tkr])), col = "blue", lwd = 2)
    abline(v=mean(data[,tkr]), untf=FALSE, col="RED")
  }
}

summary.VaR = function(data, result, data.type, title){
  require(xts)
  VaR = as.matrix(result$VaR)
  VaR = xts(VaR, order.by=as.Date(rownames(VaR), format="%Y-%m-%d"))
  data = as.matrix(data)
  data = xts(data, order.by=as.Date(rownames(data), format="%Y-%m-%d"))
  plot(as.Date(index(data)), data, type="h", col="gray", xlab="time", ylab=data.type, main=title)
  lines(index(VaR), VaR, col="red")
  legend("bottomleft", legend=c(data.type, "VaR"), col=c("gray","red"),lwd = 2, inset = 0.01, cex=0.55)
  
  #print number of violations
  str(result$VaRTest)
}

draw.VaR = function(data, VaR, data.type, title){
  require(xts)
  VaR = as.matrix(VaR)
  VaR = xts(VaR, order.by=as.Date(rownames(VaR), format="%Y-%m-%d"))
  data = as.matrix(data)
  data = xts(data, order.by=as.Date(rownames(data), format="%Y-%m-%d"))
  plot(as.Date(index(data)), data, type="h", col="gray", xlab="time", ylab=data.type, main=title)
  lines(index(VaR), VaR, col="red")
  legend("bottomleft", legend=c(data.type, "VaR"), col=c("gray","red"),lwd = 2, inset = 0.01, cex=0.55)
  
}

exclude = function(cnames, str){
  select = c()
  i=1
  for (cn in cnames){
    if(substr(cn, 1, 4)!=str){
      select[i] = cn
      i=i+1
    }
  }
  select
}

#convert assets to one portfilio column
weighted.sum = function(w, assets){
  Rp = w[1]*assets[,1]
  N = length(colnames(assets))
  for (i in 2:N){
    Rp = Rp + w[i]*assets[,i]
  }
  Rp = as.matrix(Rp)
  if(apply(Rp, 2,function(x) length(which(is.na(x)))) != 0){
    stop("There is NA in Rp which makes sd(Rp) invalid!")
  }
  Rp
}

compute.MC = function(w, returns){
  N = length(colnames(returns))
  covar = cov(returns)
  Rp = weighted.sum(w, returns)
  MC = c()
  for (i in 1:N){
    sigma = 0
    for(j in 1:N){
      sigma = sigma + w[j]*covar[i,j]
    }
    
    MC[i] = w[i]*sigma/sd(Rp)
  }
  MC
}

#funciton of computing MC and equating risk parity
rp_formula = function(w, returns = assets.ret){
  #returns = assets.ret
  #w = w.guess
  N = length(colnames(returns))
  MC = compute.MC(w, returns)
  eq = 0
  lambda = 0.0001
  a = c(1,1,1,1,
        1,1,1,1,
        1.9, 1.2, 3.4, 2.3)
  
  for(i in 1:N){
    for(j in 1:N){
      if(i != j){
        eq = eq + (MC[i] - MC[j])^2 + lambda*sum((w^2))
      }
    }
  }
  eq
}

eq1 = function(w){
  s = 0
  for(k in w){
    s = s+k
  }
  s
}

ineq = function(w){
  z = c()
  for(i in 1:length(w)){
    z[i] = w[i]
  }
  
}


lst = function(val, num){
  rep(val, times=num)
}


load.pkg <- function(x) { 
  x <- as.character(substitute(x)) 
  if(isTRUE(x %in% .packages(all.available=TRUE))) { 
    eval(parse(text=paste("require(", x, ")", sep=""))) 
  } else { 
    update.packages() 
    eval(parse(text=paste("install.packages('", x, "')", sep=""))) 
    eval(parse(text=paste("require(", x, ")", sep=""))) 
  } 
} 


VaR.Backtest = function(pf.logret=pf.logret, win.size=600, var.level = 0.95, garchOrder=NULL, armaOrder=NULL, mean=TRUE, dist="std", plot=FALSE){
  require(xts)
  require(rugarch)
  if(is.null(garchOrder) && is.null(armaOrder)){
    ##unconditional test
    #TODO
  }
  else{
    ##conditional test
    model=ugarchspec(
      variance.model = list(model = "sGARCH", garchOrder = garchOrder),
      mean.model = list(armaOrder = armaOrder, include.mean = mean),
      distribution.model = dist
      )
    ## Conditional VaR estimate
    out.sample = length(pf.logret)-win.size
    modelfit=ugarchfit(spec=model,data=pf.logret, out.sample=out.sample)
    forc1 = ugarchforecast(modelfit, n.ahead=1, n.roll = out.sample)
    VaR = t(quantile(forc1, probs=1-var.level))
    #drawing and testing null hypothesis
    
    VaR.ts = xts(VaR, order.by=as.Date(rownames(VaR)), format="%Y-%m-%d")
    pf.logret.trunc = as.matrix(pf.logret[rownames(pf.logret)>=index(VaR.ts)[1],])
    pf.logret.trunc = xts(pf.logret.trunc, order.by=as.Date(rownames(pf.logret.trunc), format="%Y-%m-%d"))
    if(plot){
      VaRplot(alpha=var.level, actual=pf.logret.trunc, VaR = VaR.ts)  
    }
    
    list(fpm = fpm(forc1),
         VaRTest = VaRTest(alpha=var.level, actual=pf.logret.trunc, VaR = VaR.ts),
         VaR = VaR.ts)
  }
}


VaR.test = function(data, VaR, var.level=0.95){
  require(xts)
  require(rugarch)
  VaR = as.matrix(VaR)
  VaR = xts(VaR, order.by=as.Date(rownames(VaR), format="%Y-%m-%d"))
  data = data[(nrow(data)-length(VaR)+1):nrow(data),]
  data = as.matrix(data)
  data = xts(data, order.by=as.Date(rownames(data), format="%Y-%m-%d"))
  if(tail(index(data),1) != tail(index(VaR),1)){
    stop("Error, the last elements of data and VaR are not the same")
  }
  
  if(length(data)!=length(VaR)){
    stop("Error, the lengths of data and VaR are not the same")
  }
  str(VaRTest(alpha=var.level, actual=data, VaR = VaR))
}

shift = function(d,k){
  len = max(nrow(d),ncol(d))
  ret = d[(1+k):len]
  ret
}


setMethod(f = "predict", signature(object = "fGARCH"), definition =
            function(object, n.ahead = 10, trace = FALSE,
                     mse = c("cond","uncond"),
                     plot=FALSE, nx=NULL, crit_val=NULL, conf=NULL, ...)
            {
              # A function implemented by Diethelm Wuertz
              
              # Description:
              #   Prediction method for an object of class fGARCH
              
              # Arguments:
              #   object    an object of class fGARCH as returned by the
              #             function garchFit().
              #   n.ahead   number of steps to be forecasted, an integer
              #             value, by default 10)
              #   trace     should the prediction be traced? A logical value,
              #             by default FALSE)
              #    mse      should the mean squared errors be conditional or unconditional
              #    plot     should the predictions be plotted
              #    nx       The number of observations to be plotted with the predictions
              #             (If plot is TRUE, the default value of nx is the sample
              #             size times 0.25.)
              #    crit_va  If you want to set manually the critical values for
              #             the confidence intervals
              #    conf     The confidence level for computing the critical values
              #             of the confidence intervals
              
              # FUNCTION:
              
              mse <- match.arg(mse)
              
              # Retrieve "fit" from Parameter Estimation:
              fit = object@fit
              
              # Get ARMA(u,v)-GARCH(p,q) Order:
              u = fit$series$order[1]
              v = fit$series$order[2]
              p = fit$series$order[3]
              q = fit$series$order[4]
              max.order = max(u, v, p, q)
              
              # Get Start Conditions:
              h.start = fit$series$h.start
              llh.start = fit$series$llh.start
              index = fit$params$index
              params = fit$params$params
              par = fit$par
              Names = names(index)
              for (Name in Names) params[Name] = par[Name]
              Names = names(params)
              
              # Retrieve From Initialized Parameters:
              cond.dist = fit$params$cond.dist
              
              # Extract the Parameters by Name:
              leverage = fit$params$leverage
              mu = params["mu"]
              if (u > 0) {
                ar = params[substr(Names, 1, 2) == "ar"]
              } else {
                ar = c(ar1 = 0)
              }
              if (v > 0) {
                ma = params[substr(Names, 1, 2) == "ma"]
              } else {
                ma = c(ma1 = 0)
              }
              omega = params["omega"]
              if (p > 0) {
                alpha = params[substr(Names, 1, 5) == "alpha"]
              } else {
                alpha = c(alpha1 = 0)
              }
              if (p > 0 & leverage) {
                gamma = params[substr(Names, 1, 5) == "gamma"]
              } else {
                gamma = c(gamma1 = 0)
              }
              if (q > 0) {
                beta  = params[substr(Names, 1, 4) == "beta"]
              } else {
                beta = c(beta1 = 0)
              }
              delta = params["delta"]
              skew = params["skew"]
              shape = params["shape"]
              
              # Trace Parameters:
              if (trace) {
                cat("\nModel Parameters:\n")
                print(c(mu, ar, ma, omega, alpha, gamma, beta, delta, skew, shape))
              }
              
              # Retrieve Series Lengths:
              M = n.ahead
              N = length(object@data)
              
              # Get and Extend Series:
              x = c(object@data, rep(mu, M))
              h = c(object@h.t, rep(0, M))
              z = c(fit$series$z, rep(mu, M))
              
              # Forecast and Optionally Trace Variance Model:
              var.model = fit$series$model[2]
              # Forecast GARCH Variance:
              if (var.model == "garch") {
                if (trace) cat("\nForecast GARCH Variance:\n")
                for (i in 1:M) {
                  h[N+i] = omega  + sum(beta*h[N+i-(1:q)])
                  for (j in 1:p) {
                    if (i-j > 0) {
                      s = h[N + i - j]
                    } else {
                      s = z[N + i - j]^2
                    }
                    h[N+i] = h[N+i] + alpha[j] * s
                  }
                }
              }
              # Forecast APARCH Variance:
              if (var.model == "aparch") {
                if (trace) cat("\nForecast APARCH Variance:\n")
                for (i in 1:M) {
                  h[N+i] = omega  + sum(beta*h[N+i-(1:q)])
                  for (j in 1:p) {
                    kappa = garchKappa(cond.dist = cond.dist, gamma = gamma[j],
                                       delta = delta, skew = skew, shape = shape)
                    if (i-j > 0) {
                      s = kappa * h[N + i - j]
                    } else {
                      s = (abs(z[N + i - j]) - gamma[j]*z[N + i - j])^delta
                    }
                    h[N+i] = h[N+i] + alpha[j] * s
                  }
                }
              }
              
              # Forecast and Optionally Trace Mean Model:
              # Note we set maxit=0 to get an object of class Arima with fixed
              #   init parameters ...
              mu <- mu/(1-sum(ar))
              ARMA <- arima(x = object@data, order = c(max(u, 1), 0, max(v, 1)),
                            init = c(ar, ma, mu), transform.pars = FALSE,
                            optim.control = list(maxit = 0))
              prediction = predict(ARMA, n.ahead)
              meanForecast = as.vector(prediction$pred)
              if(mse=="uncond") {
                meanError = as.vector(prediction$se)
              } else {
                # coefficients of h(t+1)
                a_vec <- rep(0,(n.ahead))
                hhat <- h[-(1:N)]^(2/delta[[1]]) #-> [[1]] to omit name of delta
                u2 <- length(ar)
                meanError <- hhat[1]
                a_vec[1] = ar[1] + ma[1]
                meanError <- na.omit(c(meanError,sum(hhat[1:2]*c(a_vec[1]^2,1))))
                if ((n.ahead - 1) > 1) {
                  for( i in 2:(n.ahead - 1)) {
                    a_vec[i] <- ar[1:min(u2,i-1)]*a_vec[(i-1):(i-u2)] +
                      ifelse(i>u,0,ar[i]) + ifelse(i>v,0,ma[i])
                    meanError <- na.omit(c(meanError,
                                           sum(hhat[1:(i+1)]*c(a_vec[i:1]^2,1))))
                  }
                }
                meanError <- sqrt(meanError)
              }
              if (trace) {
                cat("\nForecast ARMA Mean:\n")
                print(ARMA)
                cat("\n")
                print(prediction)
              }
              
              
              # Standard Deviations:
              standardDeviation = h^(1/delta)
              
              # Plotting the predictions
              
              if (TRUE) {
                if(is.null(nx))
                  nx <- round(length(object@data)*.25)
                t <- length(object@data)
                x <- c(object@data[(t-nx+1):t],meanForecast)
                
                # Computing the appropriate critical values
                
                if (is.null(conf))
                  conf <- 0.95
                
                if (is.null(crit_val)) {
                  if (object@fit$params$cond.dist=="norm") {
                    crit_valu <- qnorm(1-(1-conf)/2)
                    crit_vald <- qnorm((1-conf)/2)
                  }
                  if (object@fit$params$cond.dist=="snorm") {
                    crit_valu <- qsnorm(1-(1-conf)/2,xi=coef(object)["skew"])
                    crit_vald <- qsnorm((1-conf)/2,xi=coef(object)["skew"])
                  }
                  if (object@fit$params$cond.dist=="ged") {
                    crit_valu <- qged(1-(1-conf)/2,nu=coef(object)["shape"])
                    crit_vald <- qged((1-conf)/2,nu=coef(object)["shape"])
                  }
                  if (object@fit$params$cond.dist=="sged") {
                    crit_valu <- qsged(1-(1-conf)/2,nu=coef(object)["shape"],
                                       xi=coef(object)["skew"])
                    crit_vald <- qsged((1-conf)/2,nu=coef(object)["shape"],
                                       xi=coef(object)["skew"])
                  }
                  if (object@fit$params$cond.dist=="std") {
                    crit_valu <- qstd(1-(1-conf)/2,nu=coef(object)["shape"])
                    crit_vald <- qstd((1-conf)/2,nu=coef(object)["shape"])
                  }
                  if (object@fit$params$cond.dist=="sstd") {
                    crit_valu <- qsstd(1-(1-conf)/2,nu=coef(object)["shape"],
                                       xi=coef(object)["skew"])
                    crit_vald <- qsstd((1-conf)/2,nu=coef(object)["shape"],
                                       xi=coef(object)["skew"])
                  }
                  if (object@fit$params$cond.dist=="snig") {
                    crit_valu <- qsnig(1-(1-conf)/2,zeta=coef(object)["shape"],
                                       rho=coef(object)["skew"])
                    crit_vald <- qsnig((1-conf)/2,zeta=coef(object)["shape"],
                                       rho=coef(object)["skew"])
                  }
                  if (object@fit$params$cond.dist=="QMLE") {
                    e <- sort(object@residuals/object@sigma.t)
                    crit_valu <- e[round(t*(1-(1-conf)/2))]
                    crit_vald <- e[round(t*(1-conf)/2)]
                  }
                } else {
                  if (length(crit_val)==2) {
                    crit_valu <- crit_val[2]
                    crit_vald <- crit_val[1]
                  }
                  if (length(crit_val)==1) {
                    crit_valu <- abs(crit_val)
                    crit_vald <- -abs(crit_val)
                  }
                }
                
                int_l <- meanForecast+crit_vald*meanError
                int_u <- meanForecast+crit_valu*meanError
                ylim_l <- min(c(x,int_l)*(.95))
                ylim_u <- max(c(x,int_u)*(1.05))
                
                if(plot){
                  plot(x,type='l',ylim=c(ylim_l,ylim_u))
                  title("Prediction with confidence intervals")
                  lines((nx+1):(nx+n.ahead), meanForecast, col = 2, lwd = 2)
                  lines((nx+1):(nx+n.ahead), int_l, col = 3, lwd = 2)
                  lines((nx+1):(nx+n.ahead), int_u, col = 4, lwd = 2)
                  polygon(c((nx+1):(nx+n.ahead),(nx+n.ahead):(nx+1)),
                          c(int_l, int_u[n.ahead:1]),
                          border = NA, density = 20, col = 5, angle = 90)
                  es1 <- as.expression(substitute(hat(X)[t+h] + crit_valu*sqrt(MSE),
                                                  list(crit_valu=round(crit_valu,3))))
                  es2 <- as.expression(substitute(hat(X)[t+h] - crit_vald*sqrt(MSE),
                                                  list(crit_vald=abs(round(crit_vald,3)))))
                  es3 <- expression(hat(X)[t+h])
                  legend("bottomleft",c(es3,es2,es1),col=2:4,lty=rep(1,3),lwd=rep(2,3))
                  grid()  
                }
                
              }
              
              
              # Result:
              
              forecast = data.frame(
                meanForecast = meanForecast,
                meanError = meanError,
                standardDeviation = standardDeviation[-(1:N)],
                lowerInterval = int_l,
                upperInterval = int_u)
              
              
              # Return Value:
              forecast
            })


