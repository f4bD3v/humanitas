#!/usr/bin/env python2

import re
import os
import time
import subprocess as s

tweet_file = "../tweets.csv"

# Change it!!!
stanford_nlp_dir = "/home/tonyo/EPFL/big_data/sentiment_analysis/stanford-corenlp-full-2014-01-04"

def process_tweets(tweets):
    os.chdir(stanford_nlp_dir) 
    cmd_str = 'java -cp "*" -mx5g edu.stanford.nlp.sentiment.SentimentPipeline -stdin'
    proc = s.Popen([cmd_str], stdin=s.PIPE, stdout=s.PIPE, shell=True)

    # Initial probe, to avoid time measurements skews
    proc.stdin.write("\n")
    proc.stdout.readline()
    total_time = 0.0
    tweet_number = 20
    start_tweet = 100
    responses = []
    i = 1
    print "Number of tweets loaded:", tweet_number
    for t in tweets[start_tweet:start_tweet + tweet_number]:
        print "Tweet", i
        i += 1
        proc.stdin.write(t + "\n")
        t1 = time.time()
        resp = proc.stdout.readline().strip()
        print ' ', resp
        responses.append(resp)
        t2 = time.time()
        elapsed = t2 - t1
        print t2-t1
        total_time += elapsed

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
        f.readline()
        regex = re.compile(r'^(?:[^,]+,){10}(.*)$')
        for line in f:
            match = re.search(regex, line)
            if match:
                tweet_text = preprocess_tweet(match.group(1))
                tweets.append(tweet_text)

    return tweets

tweets = get_tweets()
process_tweets(tweets)

#for t in tweets:
#    print t
