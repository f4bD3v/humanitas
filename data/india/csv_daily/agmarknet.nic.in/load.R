d=as.data.frame(read.csv('india_Rice_2005-2014.csv', header=TRUE))
map=read.csv('regions.csv', header=TRUE)
#names(d) = list('date', 'freq', 'country', 'region', 'product', 'subproduct',
 #'price')
d$date = as.Date(d$date, format='%d/%m/%Y')
d$year = as.numeric(format(d$date, '%Y'))
d$day = as.numeric(format(d$date, '%j'))
d$week = as.numeric(format(d$date, '%V'))
d = d[order(d$day),] # sort by day nb
d$price = as.numeric(d$price)
d=merge(d,map)
attach(d)

tbl=table(dd$subproduct)
subprods=names(tbl[tbl>15000])
subprods=setdiff(subprods, list('Other'))

subprods_by_state = function(s) {
    cond = (dd$state == s) & (dd$subproduct %in% subprods)
    tbl = table(dd$region[cond], dd$subproduct[cond])
    return(tbl[apply(tbl, 1, sum)>0,apply(tbl,2,sum)>0])
}

subprods_by_state2 = function(s) {
    cond = (dd$state == s) & (dd$subproduct %in% subprods)
    tbl = tapply(dd$price[cond], list(dd$region[cond], dd$subproduct[cond]), mean)
    tbl[is.na(tbl)]=0
    return(tbl[apply(tbl, 1, sum)>0,apply(tbl,2,sum)>0])
}
