
# keyspaces are used to group column families together - similar to schema in RDBS
CREATE KEYSPACE tweet_collector WITH
strategy_class = 'SimpleStrategy'
AND strategy_options:replication_factor=1;
# replication_factor = 1 - no replication
# different replication requirements should reside in different keyspaces

use tweet_collector;

# In Cassandra, you define column families. 
# Column families can (and should) define metadata about the columns, 
# but the actual columns that make up a row are determined by the client application. 
# Each row can have a different set of columns. 
# Each column family should be designed to contain a single type of data.

# static column family for storing tweets
CREATE TABLE tweets (
	id int,
    time timestamp,
	user_id int,
	region text,
	city text,
    content text,
    lat float,
    long float,
   	rt_count int,
    fav_count int,
    lang text,
    PRIMARY KEY (id, time));

CREATE INDEX tweets_region
  ON tweets (region);

CREATE INDEX tweets_city
  ON tweets (city);
