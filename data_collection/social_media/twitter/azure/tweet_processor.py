import glob
import sys

from time import sleep

import tweet_db_handler

WAIT = 30000 # somewhat more than 8 min

class TweetProcessor(threading.Thread):
	
	def __init__(self, tmp_dir):
		threading.Thread.__init__(self)

		self.node = '127.0.0.1'
		self.uname = 'test-user'
		self.picklefs_proc = read_picklefs_proc()	
		self.sleep_seq_count = 0
		return


	def load_tweets(self, picklef):
		return pickle.load(open(picklef, 'rb'))

	def process_tweets(self, tweet_set):
		# filter by keywords, remove retweets, keep filtered out data (how?)
		filt_tuple = filter_tweets(tweet_set)	
		tweets_to_db = filt_tuple[0]
		tweets_to_disk = filt_tuple[1]
		for t in tweets_to_db:
			tweet_db_handler.send_tweet(t, uname, "testr", "testc")		

	def write_tweets_to_disk(self):
		# find out how to 

	def filter_tweets(self, tweet_set):
		print tweet_set
		return (0,0)

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

	def run():
		tweet_db_handler.connect(nodes)

		while True:
			if self.sleep_seq_count == 4:
				write_picklefs_proc()
				raise SystemExit("Tweetprocessor has been sleeping for about 35 minutes.\n Check progress of tweet downloader! Exiting..") 

			picklefs = glob.glob('.json')
			self.picklefs_to_proc = (set(picklefs)-set(self.picklefs_proc))
			if self.picklefs_to_proc.empty():
				self.sleep_seq_count += 1
				self.sleep_last_rnd = True
				sleep(WAIT)
				continue

			if self.sleep_last_rnd:
				self.sleep_last_rnd = False
				self.sleep_seq_count = 0 

			for picklef in self.picklefs_to_proc:
				tweet_set = load_tweets(picklef)
				process(tweet_set)

		tweet_db_handler.close()
		
def main():
	if len(sys.argv) < 2:
		print('usage: %s tweet_tmp_dir', sys.argv[0])
		
	tweet_proc_thread = TweetProcessor(sys.argv[1])
	tweet_proc_thread.start()
	

	return

if __name__ == "__main__":
	main()
