#!/usr/bin/env python2
"""
    Authors: Fabian Brix, Gabriel Grill, Anton Ovchinnikov
"""

#import tweet_db_handler 
#import SimpleClient
from SimpleClient import *
import get_category

import socket
import logging

import cPickle as pickle
import glob
import sys
import threading
import os
import random
import re
from time import sleep
import traceback

sys.path.append('keywords')
from food_categories import getFoodWordList, get_food_words, getFoodCatList

WAIT = 30000 # somewhat more than 8 min
BATCH_SIZE = 500

location_dict = {'cities': {}, 'regions': {}}

class ProcessManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.threads = []
        self.sleep_seq_count = 0
        self.sleep_last_rnd = False
        self.funcAccLock = threading.Lock()
        self.pickleAccLock = threading.Lock()
        self.picklefs_proc = self.read_picklefs_proc()	
        self.picklefs_selected = []
        
    def set_dir(self, tmp_dir):
        os.chdir(tmp_dir)

    def append_thread(self, thread):
        self.threads.append(thread)
        print 'Added tweet processor thread '+str(thread)+' to process manager'

    def append_picklefs_proc(self, picklef):
        self.picklefs_proc.append(picklef)

    def select_picklef(self):
        if not self.picklefs_to_proc:
            raise Exception('picklefs_to_proc is empty')
        picklef = random.choice(self.picklefs_to_proc)
        if picklef not in self.picklefs_selected:
            return picklef
        else:
            self.select_picklef()

    def append_picklefs_selected(self, picklef):
        self.picklefs_selected.append(picklef)

    def run(self):
        picklefs = glob.glob('*.pickle')
        self.pickleAccLock.acquire()
        self.picklefs_to_proc = list(set(picklefs)-set(self.picklefs_proc))
        #print 'First three pickle files still to process by PM ',self.picklefs_to_proc[0:3]
        self.pickleAccLock.release()
        for t in self.threads:
            t.start()
            print 'Tweet processor thread '+str(t)+' started'

        i = 0
        while True:
            picklefs = glob.glob('*.pickle')
            self.pickleAccLock.acquire()
            self.picklefs_to_proc = list(set(picklefs)-set(self.picklefs_proc))
            to_proc_len = len(self.picklefs_to_proc)
            self.pickleAccLock.release()

            if to_proc_len == 0:
                self.write_picklefs_proc()
                self.save_locations_pickle()
                raise SystemExit("No more files to process")

            i += 1
            if i == 10000:
                print len(self.picklefs_to_proc), ' remaining'
                i = 0

            """
            if self.sleep_seq_count == 4:
                write_picklefs_proc()
                raise SystemExit("Tweetprocessor has been sleeping for about 35 minutes.\n Check progress of tweet downloader! Exiting..") 

            if not to_proc_len:
                self.sleep_seq_count += 1
                self.sleep_last_rnd = True
                for t in self.threads:
                    print 'Tweet processor thread '+str(t)+' going to sleep'
                    t.force_sleep(WAIT)

                print 'PM going to sleep'
                sleep(WAIT) 
                continue

            if self.sleep_last_rnd:
                self.sleep_last_rnd = False
                self.sleep_seq_count = 0 
            """

    def read_picklefs_proc(self):
        fn = 'processed_picklefs.txt'
        picklefs = []
        if os.path.isfile(fn):
            f = open(fn, 'rb')
            if not f:
                return picklefs

                for line in f:
                    picklefs.append(line.rstrip())

            f.close()

        return picklefs

    def write_picklefs_proc(self):
		f = open('processed_picklefs.txt', 'w')
		for fn in self.picklefs_proc:
			f.write(str(fn)+'\n')

		f.close()

    def save_locations_pickle(self):
        with open('tweets_cnt_regions_cities.pick', 'wb') as f:
            pickle.dump(location_dict, f)

class TweetProcessor(threading.Thread):

    def __init__(self, proc_manager):
        threading.Thread.__init__(self)
        self.proc_manager = proc_manager
        self.proc_manager.append_thread(self)
        self.food_words = getFoodWordList()

    def force_sleep(self, WAIT):
        sleep(WAIT)

    def load_tweets(self, picklef):
        f = ''
        try:
            f = open(picklef, 'rb')
        except IOError:
            print 'cannot open', picklef
        return pickle.load(f)

    def process_tweets(self, tweet_set):
        inserts = []

        i = 0
        food_word_dict = get_food_words()
        for t in self.filter_tweets(tweet_set):
            tweet_tokens = self.get_tokens(t)
            cat_count = self.extract_features(t, tweet_tokens) 
            self.client.createInsLock.acquire()
            insert_strings = self.client.create_insert(t, tweet_tokens, food_word_dict, cat_count)
            inserts.extend(insert_strings)
            self.client.createInsLock.release()
            if len(inserts) >= BATCH_SIZE:
                self.client.sendBatchLock.acquire()
                self.client.send_batch(inserts)
                self.client.sendBatchLock.release()
                inserts = []

        if inserts:
            self.client.sendBatchLock.acquire()
            self.client.send_batch(inserts)
            self.client.sendBatchLock.release()

    def get_tokens(self, tweet):
        tweet_text_lower = tweet['text'].lower().encode("ascii","ignore")
        tweet_text_clean = re.sub('[^a-zA-Z0-9-]', ' ', tweet_text_lower)
        tweet_text_tokens = tweet_text_clean.split()
        return tweet_text_tokens

    def filter_tweets(self, tweet_set):
        for tweet in tweet_set:
            if ('text' not in tweet) or ('retweeted_status' in tweet):
                continue
            if ('user' not in tweet) or (not tweet['user']):
                continue

            # Extract week info
            if 'created_at' in tweet:
                time_obj = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
                week_str = time_obj.strftime('%U-%Y')
            else:
                week_str = 'NR'

            # Extract city/region
            city = extract_location(tweet['user']['location'], self.client.cities)
            if city != "":
                if city not in location_dict['cities']:
                    location_dict['cities'][city] = {}
                city_dict = location_dict['cities'][city]
                if week_str not in city_dict:
                    city_dict[week_str] = 0
                city_dict[week_str] += 1
                region = self.client.city_region_dict[city.lower()]
            else:
                region = extract_location(tweet['user']['location'], self.client.regions)
            if region != "":
                if region not in location_dict['regions']:
                    location_dict['regions'][region] = {}
                region_dict = location_dict['regions'][region]
                if week_str not in region_dict:
                    region_dict[week_str] = 0
                region_dict[week_str] += 1

            # Process tweet
            tweet_text_tokens = self.get_tokens(tweet)
            if (contains_words(self.food_words, tweet_text_tokens)):
                yield tweet

    def extract_features(self, t, tokens):
        category_count = {}

        prev_neg = False
        # Position in tweet
        pos = -1
        last_negation_pos = -1
        max_neg_distance = 2
        for token in tokens:
            pos += 1
            cat = get_category.get_category(token)
            if not cat: continue
            if cat[0] is 'negation':
                # Negation
                prev_neg = True
                last_negation_pos = pos
            elif cat[1] is not None:
                # Ordinary word
                cat_n = '_'.join(c for c in cat)
                if prev_neg:
                    prev_neg = False
                    if pos - last_negation_pos <= max_neg_distance:
                        # Check the distance
                        compl_cat = compl_pred_cats[cat[1]]
                        cat_n = '_'.join([cat[0],compl_cat])
                if cat_n in category_count:
                    category_count[cat_n] += 1
                else:
                    category_count[cat_n] = 1

        counts = sum(category_count.values())
        category_count['cnts'] = counts
        return category_count

    def set_client(self, client):
        self.client = client

    def run(self):
        while True:
            self.proc_manager.pickleAccLock.acquire()
            picklef = self.proc_manager.select_picklef()
            self.proc_manager.pickleAccLock.release()
            if not picklef:
                print 'picklef empty'
                continue
            #print self, ' chosen ', picklef
            print self,': loading tweets from ', picklef
            tweet_set = self.load_tweets(picklef)
            try:
                self.process_tweets(tweet_set)
            except Exception:
                traceback.print_exc()

            self.proc_manager.funcAccLock.acquire()
            self.proc_manager.append_picklefs_proc(picklef)
            self.proc_manager.funcAccLock.release()

def main(args):

    tmp_dir = args[0]
    get_category.init_reverse_index()
    food_categories = getFoodCatList()
    pred_categories = get_category.pred_categories
    get_category.extend_categories(food_categories)
    get_category.extend_categories(['cnts'])
    print get_category.c_stems
    print get_category.compl_pred_cats
    print get_category.additional_categories

    log = logging.getLogger()
    log.setLevel('INFO')
    logging.basicConfig(filename='tweet_proc.log',level=logging.DEBUG)

    node = socket.gethostbyname(socket.gethostname())
    sc = SimpleClient()
    sc.connect([node])
       
    if len(args) > 1 and args[1]=="True":
        if(args[2]=="True"):
            sc.drop_schema('tweet_collector')
        # drop_col_fam..
        sc.extended_schema(food_categories, pred_categories)
        sc.create_index(food_categories)

    sc.use_keyspace('tweet_collector')

    thread = ProcessManager() 
    thread.set_dir(tmp_dir)
    thread.start()

    threads = []

    for i in range(1):
        proc_thread = TweetProcessor(thread)
        proc_thread.set_client(sc)
        threads.append(proc_thread)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: %s tweet_tmp_dir [create_extended_schema: True]', sys.argv[0])
    else:
        main(sys.argv[1:])
