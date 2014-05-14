#get all indicators for table tweets_rice
shark-0.9.1-bin-hadoop1/bin/shark -e '
Select x.nyear, x.month, x.day, x.nregion,
round((x.predi_sum / x.tot_sum), 4),
round((x.needs_sum / x.tot_sum), 4),
round((x.senti_sum / x.tot_sum), 4),
round((x.suppl_sum / x.tot_sum), 4),
round((x.price_sum / x.tot_sum), 4),
round((x.pover_sum / x.tot_sum), 4),
x.tot_sum
From (Select COALESCE(region,"india") As nregion, year(time) As nyear, month, day, Count(*) As tot_sum,
(Sum(COALESCE(predict_inc,0)/(cnts+1)) - Sum(COALESCE(predict_dec,0)/(cnts+1))) As predi_sum,
(Sum(COALESCE(needs_high,0)/(cnts+1)) - Sum(COALESCE(needs_low,0)/(cnts+1))) As needs_sum,
(Sum(COALESCE(sentiment_positive,0)/(cnts+1)) - Sum(COALESCE(sentiment_negative,0)/(cnts+1))) As senti_sum,
(Sum(COALESCE(supply_high,0)/(cnts+1)) - Sum(COALESCE(supply_low,0)/(cnts+1))) As suppl_sum,
(Sum(COALESCE(price_high,0)/(cnts+1)) - Sum(COALESCE(price_low,0)/(cnts+1))) As price_sum,
(Sum(COALESCE(poverty_high,0)/(cnts+1)) - Sum(COALESCE(poverty_low,0)/(cnts+1))) As pover_sum

From tweet_collector.tweets_rice group by region, year(time), month, day) x
Where (x.predi_sum > 0 or x.needs_sum > 0 or x.senti_sum > 0 or x.suppl_sum > 0 or x.price_sum > 0 or x.pover_sum > 0) and x.tot_sum > 0
Order By x.nyear DESC, x.month DESC, x.day DESC, x.nregion DESC;
'

#calculate average increase and decrease tweets for rice
shark-0.9.1-bin-hadoop1/bin/shark -e '
Select x.region, x.month, x.avinc, x.avdec
From (Select region, month, AVG(COALESCE(predict_inc,0)/(cnts+1)) As avinc,  AVG(COALESCE(predict_dec,0)/(cnts+1)) As avdec From tweet_collector.tweets_rice Where year(time) == 2014 group by region, month) x
Where x.avinc > 0 or x.avdec > 0
Order By x.region DESC, x.month DESC;
'
#get amount of tweets per day about rice
Select region, year, month, day, Count(*) From tweet_collector.tweets_coriander group by region, year, month, day;

#hive function that should work, but doesn't somehow in spark
printf("2014-%i-%i", month, day)

#create database for tweet collection
create database tweet_collector;

#create table 
val table = sc.sql2rdd("Select region, year, month, day, Sum((COALESCE(needs_high,0)/cnts)) From tweet_collector.tweets_rice group by region, year, month, day")

#connect to cassandra table
CREATE EXTERNAL TABLE tweet_collector.tweets_rice (
id bigint, city string, time timestamp, lat float, long float, place string, rt_count int, fav_count int, cnts int, content string, day int, month int, region string, user_id string, year string,
needs_high int,
needs_low int,
sentiment_positive int,
sentiment_neutral int,
sentiment_negative int,
supply_high int,
supply_low int,
predict_dec int,
predict_inc int,
price_high int,
price_low int,
poverty_high int,
poverty_low int)
STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler'
WITH SERDEPROPERTIES ('cassandra.host'='100.88.224.12', 'cassandra.port'='9160');

#old - just ignore this
CREATE EXTERNAL TABLE tweet_collector.tweets ( id bigint, time timestamp, user_id string, region string, city string, content string, lat float, long float, place string, rt_count int, fav_count int, lang string, needs_high int, needs_low int, sentiment_positive int, sentiment_neutral int, sentiment_negative int, supply_high int, supply_low int, predict_dec int, predict_inc int, price_high int, price_low int, poverty_high int, poverty_low int, coriander int, coffee int, oil int, wheat int, onion int, potato int, general int, tea int, fish int, milk int, sugar int, chicken int, rice int, salt int, corn int, egg int, cnts int)
STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler'
WITH SERDEPROPERTIES ('cassandra.host'='100.88.238.59', 'cassandra.port'='9160');

CREATE EXTERNAL TABLE tweet_collector.test ( id int )
STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler'
WITH SERDEPROPERTIES ('cassandra.host'='100.88.238.59', 'cassandra.port'='9160');

CREATE EXTERNAL TABLE testi.radu3 (id bigint, time timestamp, user_id string)
STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler'
WITH SERDEPROPERTIES ('cassandra.host'='100.88.224.12', 'cassandra.port'='9160');

CREATE EXTERNAL TABLE testi.radu2 (id bigint, dd float)
STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler'
WITH SERDEPROPERTIES ('cassandra.host'='100.88.224.12', 'cassandra.port'='9160');

