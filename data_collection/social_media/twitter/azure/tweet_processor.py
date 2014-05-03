"""
    Authors: Fabian Brix, Gabriel Grill
"""

import glob
import sys

from time import sleep

import tweet_db_handler

WAIT = 30000 # somewhat more than 8 min
BATCH_SIZE = 500

class ProcessManager(threading.Thread):
    def __init__(self, tmp_dir):
		threading.Thread.__init__(self)

		self.node = '127.0.0.1'
		self.uname = 'test-user'
        self.tmp_dir = tmp_dir

		self.picklefs_proc = read_picklefs_proc()	
        
        self.threads = []

        thread1 = TweetProcessor(tmp_dir)
        thread1.start()
        self.threads.append(thread1)

        thread2 = TweetProcessor(tmp_dir)
        thread2.start()
        self.threads.append(thread2)

        thread3 = TweetProcessor(tmp_dir)
        thread3.start()
        self.threads.append(thread3)


    def run():
		tweet_db_handler.connect(nodes)

        while True:
            picklefs = glob.glob('.pickle')
            self.picklefs_to_proc = (set(picklefs)-set(self.picklefs_proc))
            if self.sleep_seq_count == 4:
                write_picklefs_proc()
                raise SystemExit("Tweetprocessor has been sleeping for about 35 minutes.\n Check progress of tweet downloader! Exiting..") 

            if self.picklefs_to_proc.empty():
                self.sleep_seq_count += 1
                self.sleep_last_rnd = True
                for t in self.threads:
                    t.sleep(WAIT)
                self.sleep(WAIT) 
                continue

            if self.sleep_last_rnd:
                self.sleep_last_rnd = False
                self.sleep_seq_count = 0 

        tweet_db_handler.close()


    def read_picklefs_proc(self):
		f = open('processed_picklefs.txt', 'rb')
		picklefs = []
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



class TweetProcessor(ProcessManager):
	
	def __init__(self, tmp_dir):
		threading.Thread.__init__(self)

		self.sleep_seq_count = 0
        self.food_words = []


	def load_tweets(self, picklef):
		return pickle.load(open(picklef, 'rb'))

	def process_tweets(self, tweet_set):
		# filter by keywords, remove retweets, keep filtered out data (how?)
		filt_tuple = filter_tweets(tweet_set)	
		tweets_to_db = filt_tuple[0]
		tweets_to_disk = filt_tuple[1]
        inserts = []

		for t in tweets_to_db:
            if len(inserts) >= BATCH_SIZE:
                tweet_db_handler.send_batch(inserts)
                inserts = []
            else:
                inserts += tweet_db_handler.create_insert(t)
			#tweet_db_handler.send_tweet(t)		

	def write_tweets_to_disk(self):
		# find out how to 

    def contains_words(to_check, tweet):
        for word in tweet:
            if (word in to_check):
                return True
        return False

	def filter_tweets(self, tweet_set):
        to_db = []
        to_disk = []

        for (tweet in tweet_set):
            if('text' in tweet and 'retweeted_status' not in tweet):
                tweet_text_lower = tweet['text'].lower()
                tweet_text_clean = ' '.join(tweet_text_lower for e in string if e.isalnum())
                tweet_text_tokens = tweet_text_clean.split()
                if(contains_words(self.food_words, tweet_text_tokens)):
                    if("user" in tweet and tweet['user'] is not None):
                        to_db += tweet
                     else:
                        to_disk += tweet
                        println("Tweet without user: " + tweet)
                        
		return (to_db, to_disk)

    def run():
		while True:
			picklef = random.choice(super.picklefs_to_proc)
			#for picklef in self.picklefs_to_proc:
            super.picklefs_proc.append(picklef)
		    tweet_set = load_tweets(picklef)
		    process(tweet_set)
		

def main():
		
    thread = ProcessManager(sys.argv[1]) 
    thread.start()

	return

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print('usage: %s tweet_tmp_dir', sys.argv[0])
        return
	main()
