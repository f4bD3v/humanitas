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
from time import sleep

sys.path.append('keywords')
from food_categories import getFoodWordList, get_food_words, getFoodCatList

WAIT = 30000 # somewhat more than 8 min
BATCH_SIZE = 500

"""
def init_stem_sets():
    categories.extend(getFoodCatList())
    for dict_name in predictors_dict:
        category_dict = predictors_dict[dict_name]
        c_stems[dict_name] = {}
        for cname in category_dict:
            categories.append(str(dict_name)+'_'+str(cname))
            word_list = category_dict[cname]
            stem_set = set()
            for word in word_list:
                stem_set.add(st.stem(word))
            c_stems[dict_name][cname] = stem_set
"""

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
        print len(self.picklefs_to_proc), ' remaining'
        self.pickleAccLock.release()
        for t in self.threads:
            t.start()
            print 'Tweet processor thread '+str(t)+' started'

        while True:
            picklefs = glob.glob('*.pickle')
            self.pickleAccLock.acquire()
            self.picklefs_to_proc = list(set(picklefs)-set(self.picklefs_proc))
            to_proc_len = len(self.picklefs_to_proc)
            self.pickleAccLock.release()
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


class TweetProcessor(threading.Thread):

    def __init__(self, proc_manager):
        threading.Thread.__init__(self)
        self.proc_manager = proc_manager
        self.proc_manager.append_thread(self)
        self.sleep_seq_count = 0
        self.food_words = getFoodWordList()
        print self.food_words

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
        # filter by keywords, remove retweets, keep filtered out data (how?)
        inserts = []

        filtered_tweets = self.filter_tweets(tweet_set)

        i = 0
        for t in filtered_tweets:
            cat_count = self.extract_features(t, tokens) 
            self.client.createInsLock.acquire()
            inserts += self.client.create_insert(t, cat_count)
            self.client.createInsLock.release()
            if len(inserts) >= BATCH_SIZE:
                self.client.sendBatchLock.acquire()
                self.client.send_batch(inserts)
                self.client.sendBatchLock.release()
                inserts = []
            i += 1

        if inserts:
            self.client.sendBatchLock.acquire()
            self.client.send_batch(inserts)
            self.client.sendBatchLock.release()

        if i > 0:
            print self, 'tweets filtered and analyzed'
        #else:
        #print self, 'no tweets matching criteria found'

    def contains_words(self, to_check, tweet):
        for word in tweet:
            if word in to_check:
                return True
        return False

    def filter_tweets(self, tweet_set):
        for tweet in tweet_set:
            if('text' in tweet and 'retweeted_status' not in tweet):
                tweet_text_lower = tweet['text'].lower()
                tweet_text_clean = ' '.join(e for e in tweet_text_lower if e.isalnum())
                tweet_text_tokens = tweet_text_clean.split()

                if(self.contains_words(self.food_words, tweet_text_tokens)):
                    if("user" in tweet and tweet['user'] is not None):
                        print 'tweet passed filter'
                        yield tweet
                    else:
                        print("Tweet not added: " + tweet)

    def extract_features(t, tokens):
        category_count = {}

        prev_neg = False
        for token in tokens:
            stem = get_category.lookup_stem_sets(token)
            if stem is None:
                raise Exception('stem not defined for '+token)

            cat = get_category.get_category(stem)
            cat_n = '_'.join(c for c in cat)
            if cat[0] is 'negation':
                prev_neg = True
            if cat[1] is not None:
                if prev_neg:
                    compl_cat = compl_pred_cats[cat[1]]
                    cat_n = '_'.join([cat[0],compl])
                if cat_n in category_count:
                    category_count[cat_n] += 1
                else:
                    category_count[cat_n] = 1

        counts = sum(category_count)
        category_count['cnts'] = counts
        return category_count

    def set_client(self, client):
        self.client = client

    def run(self):
        while True:
            """
            try:
                picklefs_to_proc = object.__getattribute__(self.base, self.picklefs_to_proc)
            except AttributeError:
                print('error')
            """

            self.proc_manager.pickleAccLock.acquire()
            picklef = self.proc_manager.select_picklef()
            self.proc_manager.pickleAccLock.release()
            if not picklef:
                print 'picklef empty'
                continue
            #print self, ' chosen ', picklef
            #for picklef in self.picklefs_to_proc:
            print 'loading tweets from ', picklef
            tweet_set = self.load_tweets(picklef)
            #print 'processing loaded tweets; see sample ->', tweet_set[0]['text']
            try:
                self.process_tweets(tweet_set)
            except Error:
                print 'something went wrong during processing'
                

            self.proc_manager.funcAccLock.acquire()
            self.proc_manager.append_picklefs_proc(picklef)
            self.proc_manager.funcAccLock.release()

def main(args):

    tmp_dir = args[0]
    get_category.init_reverse_index()
    get_category.categories.extend(getFoodCatList())
    print get_category.c_stems
    print get_category.compl_pred_cats
    print get_category.categories

    log = logging.getLogger()
    log.setLevel('INFO')
    logging.basicConfig(filename='tweet_proc.log',level=logging.DEBUG)

    node = socket.gethostbyname(socket.gethostname())
    sc = SimpleClient()
    sc.connect([node])
    sc.use_keyspace('tweet_collector')
       
    if len(args) > 1 and args[1]=="True":
         sc.extended_schema(categories)

    thread = ProcessManager() 
    thread.set_dir(tmp_dir)
    thread.start()

    threads = []

    for i in range(4):
        proc_thread = TweetProcessor(thread)
        proc_thread.set_client(sc)
        threads.append(proc_thread)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: %s tweet_tmp_dir [create_extended_schema: True]', sys.argv[0])
    else:
        main(sys.argv[1:])
