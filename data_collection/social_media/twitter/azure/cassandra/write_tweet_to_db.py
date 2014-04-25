#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cassandra.cluster import Cluster
import logging
import time
import json
import io
import sys

class SimpleClient:
    session = None

    def get(tweet, attr):
        if attr in tweet:
            return tweet[attr]
        else
            ""
    def getCoords(tweet, nr):
        if 'coordinates' in tweet and
           'coordinates' in tweet['coordinates']:
            return tweet['coordinates']['coordinates'][nr]
        else
            ""

    def send_tweet(self, t, user_id):
           self.session.execute("""
               INSERT INTO tweets (id, time, user_id, region, city, content,
                                  lat, long, rt_count, fav_count, lang)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               """,
               [get(t, "id"), get(t, "created_at"), user_id,
                get(t, "region"), get(t, "city"), get(t, "text"),
                getCoords(t, 1), #lat
                getCoords(t, 0), #long
                get(t, "retweet_count"), get(t, "favorite_count"),
                get(t, "lang")
               ]
           )
        log.info("tweets loaded into db")

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
            CREATE KEYSPACE tweet_collector WITH
            strategy_class = 'SimpleStrategy'
            AND strategy_options:replication_factor=1;""")

        self.session.execute("use tweet_collector;")

        self.session.execute("""
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
        """)
        log.info("Schema created.")

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

    def print_rows(self):
        results = self.session.execute("SELECT * FROM tweets")
        print("Tweet table:")
	print("---------------------------------------------------------------")
        for row in results:
            print(row)
        log.info("Rows printed.")

def open_tweets(fname):
    with open(fname) as f:
        try:   
            for line in f.readlines():
                yield (json.loads(line.decode('utf8')), line)
        except Exception as e:
            print("Failed on {0}: {1}".format(fname, e))

def usage():
    print '''python %s <input file> [node] [user]
    Defaults: node = 127.0.0.1
              user = test-user
    stores tweets read from input file into a local cassandra db''' % sys.argv[0]

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
    client.create_schema()
    time.sleep(10)
    client.create_index()
    time.sleep(10)

    for t in open_tweets(sys.argv[1]):
        client.send_tweet(t, uname)

    client.print_rows()
    client.close()


if __name__ == '__main__':
    main()
