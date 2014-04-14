d = NULL
for (x in 2005:2014) {
    dd=as.data.frame(read.csv(
        paste('all_commodities_weekly_india_',x,'.csv',sep=''), header=FALSE))
    if (is.null(d)) d=dd
    else d=rbind(d,dd)
}

names(d) = list('date', 'freq', 'country', 'region', 'product', 'subproduct',
             'price')
d$date = as.Date(d$date, format='%d/%m/%Y')
d$year = as.numeric(format(d$date, '%Y'))
d$week = as.numeric(format(d$date, '%V'))
d = d[order(d$week),] # sort by week nb
attach(d)

# multiple subproducts in the same (week, region, product) tuple, average them


allpairs = function(l)
{
    ll = levels(l)
    for (i in 1:length(ll))
        for (j in (i+1):length(ll)) {
            cat(paste('Correlation between',ll[i],' and ',ll[j],':',
                cor(price[l==ll[i]], price[l==ll[j]]), '\n')
            )
        }
}

# compute correlation coefficient between all pairs of regions
#allpairs(region)

# compute correlation coefficient between all pairs of products
#allpairs(product)

# show the number of subproducts for each product
nb_subprods_by_prod = function()
{
    x=tapply(d$subproduct, d$product, function(r){ sum(table(r)>0) })
    # x[x>1] to return only those >1
    return(x)
}

# find all the subproducts of a given product
subprods_of = function(p) {
 x=table(d$subproduct[d$product==p])
 #x=sapply(levels(subproduct), function(sp){ sum((product==p) * (subproduct == sp)) } )
 return(x[x>1])
}

