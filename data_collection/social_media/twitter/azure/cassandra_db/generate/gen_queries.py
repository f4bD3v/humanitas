#!/usr/bin/env python2

import sys
import os
import re

template_create = """
CREATE EXTERNAL TABLE tweet_collector.%s (
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
"""

template_select =  """
SELECT x.nyear, x.month, x.day, x.nregion,
ROUND((x.predi_sum / x.tot_sum), 4),
ROUND((x.needs_sum / x.tot_sum), 4),
ROUND((x.senti_sum / x.tot_sum), 4),
ROUND((x.suppl_sum / x.tot_sum), 4),
ROUND((x.price_sum / x.tot_sum), 4),
ROUND((x.pover_sum / x.tot_sum), 4),
x.tot_sum
FROM ( SELECT COALESCE(region,"india") AS nregion, year(time) AS nyear, month, day, COUNT(*) AS tot_sum,
    (SUM(COALESCE(predict_inc,0)/(cnts+1))          - SUM(COALESCE(predict_dec,0)/(cnts+1)))        AS predi_sum,
    (SUM(COALESCE(needs_high,0)/(cnts+1))           - SUM(COALESCE(needs_low,0)/(cnts+1)))          AS needs_sum,
    (SUM(COALESCE(sentiment_positive,0)/(cnts+1))   - SUM(COALESCE(sentiment_negative,0)/(cnts+1))) AS senti_sum,
    (SUM(COALESCE(supply_high,0)/(cnts+1))          - SUM(COALESCE(supply_low,0)/(cnts+1)))         AS suppl_sum,
    (SUM(COALESCE(price_high,0)/(cnts+1))           - SUM(COALESCE(price_low,0)/(cnts+1)))          AS price_sum,
    (SUM(COALESCE(poverty_high,0)/(cnts+1))         - SUM(COALESCE(poverty_low,0)/(cnts+1)))        AS pover_sum
    FROM tweet_collector.%s GROUP BY region, year(time), month, day) x
WHERE (x.predi_sum > 0 or x.needs_sum > 0 or x.senti_sum > 0 or x.suppl_sum > 0 or x.price_sum > 0 or x.pover_sum > 0) 
       and (x.tot_sum > 0)
ORDER BY x.nyear DESC, x.month DESC, x.day DESC, x.nregion DESC;
"""


categories = ['coriander', 'coffee', 'oil', 'wheat', 'onion', 'potato', 'general', 'tea', 'fish', 'milk', 'sugar', 'chicken', 'rice', 'salt', 'corn', 'egg']


tmp_file = '/tmp/query.tmp'

def save_tmp(s):
    with open(tmp_file, 'wb') as f:
	    f.write(s)

def gen_query_select(cat):
    table_name = 'tweets_' + cat
    return template_select % (table_name)

def gen_query_create(cat):
    table_name = 'tweets_' + cat
    return template_create % (table_name)

def execute_query(cat, query):
    save_tmp(query)
    cmd = "./shark-0.9.1-bin-hadoop1/bin/shark -e '' -i %s" % (tmp_file)
    output = os.popen(cmd).read()
    return output

for cat in categories:
    query_create = gen_query_create(cat)
    print '### CREATE query for', cat
    execute_query(cat, query_create)
    query_select = gen_query_select(cat)
    print '### SELECT query for', cat
    result = execute_query(cat, query_select)
    result = re.sub(r'\t', ',', result)
    result = "\n".join(result.split("\n")[3:])
    with open('./shark_out/shark_out_' + cat + '.csv', 'wb') as f:
        f.write(result)

