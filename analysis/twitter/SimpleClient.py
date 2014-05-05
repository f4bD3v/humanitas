"""
    Authors: Gabriel Grill
"""


#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cassandra.cluster import Cluster
import logging
import time
import json
import io
import sys
import csv
import os
from datetime import date, datetime
import threading

log = logging.getLogger()
log.setLevel('INFO')

def extract_features(t, col_str, val_str):
    tweet_text_lower = tweet['text'].lower()
    tweet_text_clean = ' '.join(tweet_text_lower for e in string if e.isalnum())
    tweet_text_tokens = tweet_text_clean.split()
    category_count = {}

    for token in tweet_text_tokens:
        cat = getCategory(token)
        if cat != "":
            if cat in category_count:
                category_count[cat] += 1
            else:
                category_count[cat] = 0

    for cat, count in category_count.iteritems():
           col_str.append(cat)
           val_str.append(count)

def load_location_dict(fname):
    #path = os.path.split(os.getcwd())[0]
    #path = os.getcwd()
    #fname = path+"/cassandra_db/"+str(fname)
    print fname
    with open(fname, 'r') as ifile:
        reader = csv.reader(ifile)
        print reader
        next(reader, None) #ignore header
        return {rows[0].lower():rows[1].lower() for rows in reader}

def extract_location(loc, locs):
    loc_tokens = ' '.join(loc.lower() for e in string if e.isalnum()).strip().split()

    for token in loc_tokens:
        if token.lower() in locs:
            return token
    return ""

#prepares 'text' values for the db
def prep(x):
    #return "'" + x + "'"
    return "'" + ''.join(e for e in string if e.isalnum()) + "'"
    #return "'" + x.encode("ascii","ignore").replace("'", "") + "'"

#tweet contains field with content
def has(t, val):
    return val in t and t[val] is not None

#reads tweets from a text file
def open_tweets(fname):
    with open(fname) as f:
        try:   
            for line in f.readlines():
                yield json.loads(line.decode('utf8'))
        except Exception as e:
            print("Failed on {0}: {1}".format(fname, e))

class SimpleClient:
    #the CQL standard can be found here: https://github.com/pcmanus/cassandra/blob/3779/doc/cql3/CQL.textile
    #the api to this cassandra lib can be found here: http://www.datastax.com/documentation/developer/python-driver/1.0/share/doctips/docTips.html
    session = None

    cols = ["id", "time", "user_id", "region", "city", "content",
            "lat", "long", "rt_count", "fav_count", "lang"]
 
    tweet_cols = [("id", "id", False), ("content", "text", True),
                  ("rt_count", "retweet_count", False),
                  ("fav_count", "favorite_count", False), ("lang", "lang", True)]
    city_region_dict = load_location_dict('regions.csv')
    regions = set(city_region_dict.values())
    cities = city_region_dict.keys()

    def __init__(self):
        self.createInsLock = threading.RLock()
        self.sendBatchLock= threading.RLock()

    #takes as input a list of insert statements and sends them as a batch
    #very fast, but batch construction and sending should be best done in a
    #seperate thread for max. performance
    def send_batch(self, inserts):
        log.info("invoking batch execution insert")
        self.session.execute("BEGIN BATCH\n" + "\n".join(inserts) + "\nAPPLY BATCH;")
        log.info("batch of tweets loaded into db")

    #returns a string representing an insert for a tweet
    def create_insert(self, t, cat_counts=None):
       log.info("creating insert")
       col_str = []
       val_str = []
       city = ""
       region = ""

       for col, val, shouldPrep in self.tweet_cols:
           if has(t,val):
               col_str.append(col)
               if(shouldPrep):
                   val_str.append(prep(t[val]))
               else:
                   val_str.append(str(t[val]))

       if has(t,'user'):
           if has(t['user'], 'id'):
               col_str.append('user_id')
               val_str.append(prep(t['user']['id']))
           if has(t['user'],'location'):
               city = extract_location(tweet['user']['location'], self.cities)
               if city != "":
                  region = self.city_region_dict[city]
               else:
                  region = extract_location(tweet['user']['location'], self.regions)

       if has(t,'place') and has(t['place'],'name'):
           col_str.append("place")
           val_str.append(prep(t['place']['name']))

       if(region != ""):
           col_str.append("region")
           val_str.append(prep(region))
       if(city != ""):
           col_str.append("city")
           val_str.append(prep(city))

       if has(t,'coordinates') and has(t['coordinates'],'coordinates'):
           col_str.append("long")
           val_str.append(str(t['coordinates']['coordinates'][0]))
           col_str.append("lat")
           val_str.append(str(t['coordinates']['coordinates'][1]))
       if has(t,"created_at"):
            col_str.append("time")
            val_str.append(prep(time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(t['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))))

       #extract_features(t, col_str, val_str)
       if cat_counts is not None:
        for cat, count in category_count.iteritems():
            col_str.append(cat)
            val_str.append(count)

       return "INSERT INTO tweets (" + ",".join(col_str) + ") VALUES (" + ",".join(val_str) + ");"

    #inserts a tweet into the db
    def send_tweet(self, t):
        s = self.create_insert(t)
        self.session.execute(s)
        log.info("tweet loaded into db")

    #connect to cluster
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

    def use_keyspace(self, keyspace):
        self.session.execute("use "+str(keyspace)+";")
        log.info("Using keyspace "+str(keyspace))

    def extended_schema(self, categories):
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
            place text,
   	        rt_count int,
            fav_count int,
            lang text,\n""" +
            ',\n'.join(map((lambda coln: str(coln) + " int"), categories))
            + """PRIMARY KEY (id, time));
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

    #prints all saved tweets
    def print_rows(self):
        results = self.session.execute("SELECT * FROM tweets;")
        print("Tweet table:")
        print("---------------------------------------------------------------")
        for row in results:
            print(row)
        log.info("Rows printed.")

def usage():
    print("""python %s <input file | -d> [node]
              -d     drop schema

    Defaults: node = 127.0.0.1
    stores tweets read from input file into a local cassandra db"""
    % sys.argv[0])

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)

    node = "127.0.0.1"
    if len(sys.argv) > 2:
        node = sys.argv[2]

    logging.basicConfig()
    client = SimpleClient()
    client.connect([node])

    if sys.argv[1] == "-d":
        client.drop_index()
        client.drop_schema()
        exit(0)

    client.create_schema([])
    client.create_index()

    for t in open_tweets(sys.argv[1]):
        client.send_tweet(t)

    client.print_rows()
    client.close()


if __name__ == '__main__':
    main()
