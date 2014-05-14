

Select id From tweet_collector.tweets_rice Where year = 2014 Limit 20;
Select id, Sum(year) From tweet_collector.tweets_rice Group By id, year Limit 20;

Select * From tweet_collector.tweets LIMIT 2;
create database tweet_collector;

Select region, year, month, day, Count(*) From tweet_collector.tweets_coriander group by region, year, month, day;

Select region, month, day, Sum((COALESCE(predict_dec,0)/cnts)) As sum_predict_dec From tweet_collector.tweets_rice Where year(time) == 2014 group by region, month, day Having sum_predict_dec > 0  Order By region DESC, month DESC, day DESC;

Select region, year, month, day, Sum((COALESCE(needs_high,0))) As sum_highn From tweet_collector.tweets_rice group by region, year, month, day Having sum_highn > 0;

Select year, month, day, Sum(COALESCE(predict_dec,0)) As sum_highn From tweet_collector.tweets_rice group by year, month, day Having sum_highn > 0;


Select Count(*) From tweet_collector.tweets_rice group by year, month, day Having Sum(COALESCE(predict_dec,0)) > 0;

val table = sc.sql2rdd("Select region, year, month, day, Sum((COALESCE(needs_high,0)/cnts)) From tweet_collector.tweets_rice group by region, year, month, day")

#connect to table
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
