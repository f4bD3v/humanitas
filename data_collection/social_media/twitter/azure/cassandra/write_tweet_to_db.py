#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cassandra.cluster import Cluster
import logging
import time
import json
import io
import sys
from datetime import date, datetime

log = logging.getLogger()
log.setLevel('INFO')

def get(tweet, attr):
    if (attr in tweet):
        return tweet[attr]
    else:
        return ""
def getCoords(tweet, nr):
    if ('coordinates' in tweet and tweet['coordinates'] is not None and
      'coordinates' in tweet['coordinates']):
        return tweet['coordinates']['coordinates'][nr]
    else:
        return ""

def prep(x):
    return "'" + x.encode("ascii","ignore").replace("'", "") + "'"

def open_tweets(fname):
    with open(fname) as f:
        try:   
            for line in f.readlines():
                yield json.loads(line.decode('utf8'))
        except Exception as e:
            print("Failed on {0}: {1}".format(fname, e))

class SimpleClient:
    session = None
    cols = ["id", "time", "user_id", "region", "city", "content",
            "lat", "long", "rt_count", "fav_count", "lang"]
    tweet_cols = [("id", "id", False), ("content", "text", True),
                  ("rt_count", "retweet_count", False),
                  ("fav_count", "favorite_count", False), ("lang", "lang", True)]

    def send_batch(self, inserts):
	self.session.execute("BEGIN BATCH\n" + inserts + "\nAPPLY BATCH;")
        log.info("batch of tweets loaded into db")

    def create_insert(self, t, user_id, region, city):
       col_str = ["user_id", "region", "city"]
       val_str = [prep(user_id), prep(region), prep(city)]
       for (col, val, shouldPrep) in self.tweet_cols:
           if val in t:
               col_str.append(col)
               if(shouldPrep):
                   val_str.append(prep(t[val]))
               else:
                   val_str.append(str(t[val]))
       if ('coordinates' in t and t['coordinates'] is not None and
          'coordinates' in t['coordinates']):
           col_str.append("long")
           val_str.append(str(t['coordinates']['coordinates'][0]))
           col_str.append("lat")
           val_str.append(str(t['coordinates']['coordinates'][1]))
       if "created_at" in t:
            col_str.append("time")
            val_str.append(prep(time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(t['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))))
       return "INSERT INTO tweets (" + ",".join(col_str) + ") VALUES (" + ",".join(val_str) + ");"

    def send_tweet(self, t, user_id, region, city):
        '''
	timestamp = ""
	if "created_at" in t:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(t['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            #time.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y").isoformat()
        print(t["id"])

        print( [get(t, "id"), timestamp, 
             user_id, region, city, get(t, "text"),
             getCoords(t, 1), #lat
             getCoords(t, 0), #long
             get(t, "retweet_count"), get(t, "favorite_count"),
             get(t, "lang")
            ])
        self.session.execute("""
            INSERT INTO tweets (id, time, user_id, region, city, content,
                                lat, long, rt_count, fav_count, lang)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [get(t, "id"), timestamp, user_id,
             region, city, get(t, "text"),
             getCoords(t, 1), #lat
             getCoords(t, 0), #long
             get(t, "retweet_count"), get(t, "favorite_count"),
             get(t, "lang")
            ])
        '''
        s = self.create_insert(t, user_id, region, city)
        print(s)
        self.session.execute(s)
        log.info("tweet loaded into db")

    def connect(self, nodes):
        cluster = Cluster(nodes)
        metadata = cluster.metadata
        self.session = cluster.connect()
        log.info("Connected to cluster: " + metadata.cluster_name)
        for host in metadata.all_hosts():
            log.info("Datacenter: %s; Host: %s; Rack: %s",
                host.datacenter, host.address, host.rack)

    def close(self):
        self.session.cluster.shutdown()
        self.session.shutdown()
        log.info("Connection closed.")

    def create_schema(self):
        self.session.execute("""
            CREATE KEYSPACE tweet_collector WITH replication =
            {'class':'SimpleStrategy', 'replication_factor':1};""")

        self.session.execute("use tweet_collector;")

        self.session.execute("""
            CREATE TABLE tweets (
	        id bigint,
                time timestamp,
	        user_id text,
	        region text,
	        city text,
                content text,
                lat float,
                long float,
   	        rt_count int,
                fav_count int,
                lang text,
                PRIMARY KEY (id, time));
        """)
        log.info("Schema created.")

    def drop_schema(self):
        self.session.execute("DROP TABLE tweet_collector.tweets;")
        self.session.execute("DROP KEYSPACE tweet_collector;")

    def create_index(self):
        self.session.execute("""
            CREATE INDEX tweets_region
            ON tweets (region);
        """)
        self.session.execute("""
            CREATE INDEX tweets_city
            ON tweets (city);
        """)
        log.info("Index created.")

    def drop_index(self):
        self.session.execute("use tweet_collector;")
        self.session.execute("DROP INDEX tweets_city;")
        self.session.execute("DROP INDEX tweets_region;")

    def print_rows(self):
        results = self.session.execute("SELECT * FROM tweets")
        print("Tweet table:")
        print("---------------------------------------------------------------")
        for row in results:
            print(row)
        log.info("Rows printed.")

def usage():
    print("""python %s <input file | -d> [node] [user]
              -d     drop schema

    Defaults: node = 127.0.0.1
              user = test-user
    stores tweets read from input file into a local cassandra db"""
    % sys.argv[0])

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    uname = "test-user"
    node = "127.0.0.1"
    if len(sys.argv) > 2:
        node = sys.argv[2]
    if len(sys.argv) > 3:
        uname = sys.argv[3]

    logging.basicConfig()
    client = SimpleClient()
    client.connect([node])

    if sys.argv[1] == "-d":
        client.drop_index()
        client.drop_schema()
        exit(0)

    client.create_schema()
    client.create_index()

    for t in open_tweets(sys.argv[1]):
        client.send_tweet(t, uname, "testr", "testc")

    client.print_rows()
    client.close()


if __name__ == '__main__':
    main()
