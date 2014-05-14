#!/usr/bin/env python2

import re
import os
import sys
import time
import random
import pickle
import subprocess as s

tweet_file = "tweets.pickle"

# Change it!!!
### Stanford NLP params
stanford_nlp_dir = '/home/tonyo/EPFL/big_data/sentiment_analysis/stanford-corenlp-full-2014-01-04'
stanford_nlp_str = 'java -cp "*" -mx5g edu.stanford.nlp.sentiment.SentimentPipeline -stdin'

### SentiStrength params
sentistrength_dir = '/home/tonyo/EPFL/big_data/sentiment_analysis/SentiStrength'
sentistrength_str = 'java -jar SentiStrength.jar sentidata ./SentiStrength_data/ cmd trinary'

def process_response(r, method):
    if method == 'stanford':
        return r
    elif method == 'sentistrength':
        return r.split()[2] 
    else:
        sys.exit("Invalid classification method:", method)
    return "Smth invalid"


def process_tweets(tweets, method):
    if method == 'stanford':
        working_dir = stanford_nlp_dir
        cmd_str = stanford_nlp_str
    elif method == 'sentistrength':
        working_dir = sentistrength_dir
        cmd_str = sentistrength_str
    else:
        raise "Invalid classification method!"

    os.chdir(working_dir) 
    proc = s.Popen([cmd_str], stdin=s.PIPE, stdout=s.PIPE, shell=True)

    # Initial probe, to avoid time measurements skews
    proc.stdin.write("\n")
    proc.stdout.readline()
    total_time = 0.0
    tweet_number = 1000
    start_tweet = 100
    responses = []
    i = 1
    print "Number of tweets loaded:", tweet_number
    for t in tweets[start_tweet:start_tweet + tweet_number]:
        print "Tweet", i
        print t
        t1 = time.time()
        proc.stdin.write(t + "\n")
        resp = proc.stdout.readline().strip()
        resp = process_response(resp, method)
        print ' ', resp
        responses.append(resp)
        t2 = time.time()
        elapsed = t2 - t1
        print t2-t1
        total_time += elapsed
        i += 1

    try:
        proc.kill()
    except OSError:
        # can't kill a dead proc
        pass

    avg_per_tweet = total_time / tweet_number
    print "Elapsed time:", total_time
    print "Average time per tweet:", avg_per_tweet
    print "Average speed:", 60 / avg_per_tweet, "(tweets/min)", \
                            3600 / avg_per_tweet, "(tweets/hour)"
    return

def preprocess_tweet(tweet):
    tweet = tweet.replace("\n", '')
    tweet = tweet.replace("\r", '')
    return tweet

def get_tweets():
    tweets = []
    with open(tweet_file, 'r') as f:
        tweet_data = pickle.load(f)
        random.shuffle(tweet_data)
        for data in tweet_data:
            tweet_text = data['text']
            if re.search(r'^\s*http\S*://\S+\s*$', tweet_text):
                continue
            try: 
                tweet_text.decode('ascii')
            except UnicodeEncodeError:
                continue
            tweets.append(tweet_text)

    return tweets


if __name__ == '__main__':
    tweets = get_tweets()
    if len(sys.argv) != 2:
        method = 'sentistrength'
    else:
        method = sys.argv[1]
    process_tweets(tweets, method)

