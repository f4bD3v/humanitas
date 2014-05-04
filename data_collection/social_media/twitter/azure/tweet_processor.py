"""
    Authors: Fabian Brix, Gabriel Grill
"""

#import tweet_db_handler 
#import SimpleClient
from SimpleClient import *

import pickle
import glob
import sys
import threading
import os
import random

from time import sleep

#from cassandra_db.tweet_db_handler import SimpleCluster
#from cassandra_db.tweet_db_handler import SimpleCluster

WAIT = 30000 # somewhat more than 8 min
BATCH_SIZE = 500

class ProcessManager(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.threads = []
        self.sleep_seq_count = 0
        self.sleep_last_rnd = False

        self.picklefs_proc = self.read_picklefs_proc()	
        
    def set_dir(self, tmp_dir):
        os.chdir(tmp_dir)

    def append_thread(self, thread):
        self.threads.append(thread)
        print 'Added tweet processor thread '+str(thread)+' to process manager'

    def get_picklefs_to_proc(self):
        to_proc = self.picklefs_to_proc
        return to_proc

    def append_picklefs_proc(self, picklef):
        self.picklefs_proc.append(picklef)

    def run(self):
        picklefs = glob.glob('*.pickle')
        self.picklefs_to_proc = list(set(picklefs)-set(self.picklefs_proc))
        print 'First three pickle files still to process by PM ',self.picklefs_to_proc[0:3]
        print len(self.picklefs_to_proc), ' remaining'
        for t in self.threads:
            t.start()
            print 'Tweet processor thread '+str(t)+' started'

        while True:
            picklefs = glob.glob('.pickle')
            self.picklefs_to_proc = (set(picklefs)-set(self.picklefs_proc))
            if self.sleep_seq_count == 4:
                write_picklefs_proc()
                raise SystemExit("Tweetprocessor has been sleeping for about 35 minutes.\n Check progress of tweet downloader! Exiting..") 

            if len(self.picklefs_to_proc):
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
        self.food_words = []

    def force_sleep(self):
        sleep(WAIT)

    def load_tweets(self, picklef):
        print os.getcwd()
        f = ''
        try:
            f = open(picklef, 'rb')
        except IOError:
            print 'cannot open', picklef
        return pickle.load(f)

    def process_tweets(self, tweet_set):
        # filter by keywords, remove retweets, keep filtered out data (how?)
        tweets_to_db = self.filter_tweets(tweet_set)	
        inserts = []

        for t in tweets_to_db:
            if len(inserts) >= BATCH_SIZE:
                self.client.send_batch(inserts)
                inserts = []
            else:
                inserts += self.client.create_insert(t)
			#db.send_tweet(t)		

    def contains_words(self, to_check, tweet):
        for word in tweet:
            if (word in to_check):
                return True
        return False

    def filter_tweets(self, tweet_set):
        to_db= []
        to_disk = []
        for tweet in tweet_set:
            if('text' in tweet and 'retweeted_status' not in tweet):
                tweet_text_lower = tweet['text'].lower()
                tweet_text_clean = ' '.join(e for e in tweet_text_lower if e.isalnum())
                tweet_text_tokens = tweet_text_clean.split()

                if(self.contains_words(self.food_words, tweet_text_tokens)):
                    if("user" in tweet and tweet['user'] is not None):
                        to_db += tweet
                    else:
                        to_disk += tweet
                        println("Tweet without user: " + tweet)
                        
		return to_db 

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
            picklefs_to_proc = self.proc_manager.get_picklefs_to_proc()
            if not picklefs_to_proc:
                continue
            picklef = random.choice(picklefs_to_proc)
            print self, ' chosen ', picklef
            #for picklef in self.picklefs_to_proc:
            self.proc_manager.append_picklefs_proc(picklef)
            print 'loading tweets from ', picklef
            tweet_set = self.load_tweets(picklef)
            print 'processing loaded tweets; see sample ->', tweet_set[0:3]
            self.process_tweets(tweet_set)

def main():
    sc = SimpleClient()
    node = "127.0.0.1"
    sc.connect([node])
    thread = ProcessManager() 
    thread.set_dir(sys.argv[1])
    thread.start()

    threads = []

    thread1 = TweetProcessor(thread)
    threads.append(thread1)

    thread2 = TweetProcessor(thread)
    threads.append(thread2)

    thread3 = TweetProcessor(thread)
    threads.append(thread3)

    for t in threads:
        t.set_client(sc)

    sc.close()



if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('usage: %s tweet_tmp_dir', sys.argv[0])
	main()
