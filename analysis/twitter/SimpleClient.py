#!/usr/bin/env python2

"""
    Authors: Gabriel Grill, Anton Ovchinnikov
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
import re
from time import sleep

log = logging.getLogger()
log.setLevel('INFO')

DEFAULT_TIMEOUT = 300.0

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
    text = re.sub('[^a-zA-Z0-9-]', ' ', loc.encode("ascii","ignore")).lower()
    loc_tokens = filter(lambda a: a != '', text.strip().split())

    if loc_tokens is not None:
        for token in locs:
            if token in loc_tokens:
                return token
    return ""

#prepares 'text' values for the db
def prep(x):
    #return "'" + x + "'"
    text = re.sub('[^a-zA-Z0-9:-]', ' ', re.sub("-+", "-", x.encode("ascii","ignore")))
    return "'" + text + "'"
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

def contains_words(to_check, tweet_tokens):
    for word in tweet_tokens:
        if word in to_check:
            return True
    return False

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

    def create_insert(self, t, t_tokens, food_word_dict, cat_counts=None):
        insert_strs = []
        for food_category in food_word_dict:
            category_words = food_word_dict[food_category]
            for product in category_words:
                if contains_words([product], t_tokens):
                    insert_string = self.create_insert_for_category(t, food_category, cat_counts)
                    insert_strs.append(insert_string)
        return insert_strs 

    #returns a string representing an insert for a tweet
    def create_insert_for_category(self, t, food_category, cat_counts=None):
       log.info("creating insert")
       col_str = []
       val_str = []
       city = ""
       region = ""

       for col, val, shouldPrep in self.tweet_cols:
           if has(t,val):
               col_str.append(col)
               if(shouldPrep):
                   val = prep(t[val])
               else:
                   val = str(t[val])
               val_str.append(val.strip())

           
       if has(t,'user'):
           if has(t['user'], 'id'):
               col_str.append('user_id')
               val_str.append(prep(str(t['user']['id'])))
           if has(t['user'],'location'):
               city = extract_location(t['user']['location'], self.cities)
               if city != "":
                  region = self.city_region_dict[city.lower()]
               else:
                  region = extract_location(t['user']['location'], self.regions)

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
            time_obj = datetime.strptime(t['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            val_str.append(prep(time_obj.strftime('%Y-%m-%d %H:%M:%S')))
            col_str.append('day')
            val_str.append(str(time_obj.day))
            col_str.append('month')
            val_str.append(str(time_obj.month))
            col_str.append('year')
            val_str.append(str(time_obj.year))

       #extract_features(t, col_str, val_str)
       if cat_counts is not None:
        for cat, count in cat_counts.iteritems():
            col_str.append(cat)
            val_str.append(str(count))

       table_name = 'tweets_' + food_category
       return "INSERT INTO " + table_name + "(" + ",".join(col_str) + ") VALUES (" + ",".join(val_str) + ");"

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
        self.session.default_timeout = DEFAULT_TIMEOUT
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

    def extended_schema(self, food_categories, pred_categories):
        self.session.execute("""
            CREATE KEYSPACE tweet_collector WITH replication =
            {'class':'SimpleStrategy', 'replication_factor':1};""")
        log.info('Created keyspace tweet_collector')

        sleep(3)
        self.session.execute("use tweet_collector;")

        create_table_strs = []
        for f_category in food_categories:
            table_name = 'tweets_' + f_category
            te = """
                 CREATE TABLE %s (
    	         id bigint,
                 time timestamp,
                 day int,
                 month int,
                 year int,
    	         user_id text,
    	         region text,
    	         city text,
                 content text,
                 lat float,
                 long float,
                 place text,
       	         rt_count int,
                 fav_count int,
                 cnts int,
                 lang text,\n""" %(table_name) + \
                 ',\n'.join(map((lambda coln: str(coln) + " int"), pred_categories)) + ',\n' + \
                 "PRIMARY KEY (id) );"
            print("Map: " + te)
            self.session.execute(te)
            create_table_strs.append(te)
            log.info("> Table " + table_name + " created.")
            sleep(1)
        log.info(">>> Schema created.")

        # Save 'create table' queries
        with open('shark_create_table.sql', 'wb') as f:
            for s in create_table_strs:
                s = re.sub(r'\btext\b', 'string', s)
                s = re.sub(r'CREATE TABLE', 'CREATE EXTERNAL TABLE', s)
                s = re.sub(r',\nPRIMARY KEY.*$', ")\n", s)
                s += "STORED BY 'org.apache.hadoop.hive.cassandra.cql.CqlStorageHandler' WITH SERDEPROPERTIES ('cassandra.host'='100.88.224.12', 'cassandra.port'='9160');"
                f.write(s + "\n")

    def drop_schema(self, keyspace):
        self.session.execute("DROP KEYSPACE IF EXISTS tweet_collector;")
        print "Schema (keyspace) dropped."

    def create_index(self, food_categories):
        for category in food_categories:
            table_name = 'tweets_' + category
            for column in ['region', 'city', 'time', 'long', 'lat']:
                index_name = table_name + '_' + column
                create_str = """
                    CREATE INDEX %s
                    ON %s (%s);""" % (index_name, table_name, column)
                print create_str
                self.session.execute(create_str)
                sleep(3)
                log.info("> Index %s on table %s created." % (index_name, table_name) )

        log.info(">>> Index created.")

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
        client.drop_schema()
        exit(0)

    #client.create_schema([])
    #client.create_index()

    for t in open_tweets(sys.argv[1]):
        client.send_tweet(t)

    client.print_rows()
    client.close()


if __name__ == '__main__':
    main()
