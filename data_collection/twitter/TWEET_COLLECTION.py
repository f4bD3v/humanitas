from twython import Twython, TwythonError, TwythonRateLimitError
from datetime import datetime
from time import sleep
from sys import maxint
import re
import csv
import sys
import pickle

APP_KEY = 'aylam3pBvHkhOUmycOWw'
APP_SECRET = 'uXAuZwGX8FUno0P54gdIlGnkijhkY56lVFxRwgjgI'
root = "KareenaOnline"

RATE_LIMIT_WINDOW = 15 * 60
TWEET_BATCH_SIZE = 200
FOLLOWER_RATE_LIMIT = 30
FOLLOWER_BATCH_SIZE = 200
TWEET_RATE_LIMIT = 300
MIN_TWEETS = 50
MAX_TWEETS = 3200
MAX_FOLLOWERS = 1000000

def get_all_locations_in_india():
    yield 'india'
    with open('cities-in-india.txt', 'r') as f:
        for line in map(lambda x:re.split(r'[\s\t]+', x), f.readlines()):
            if len(line) != 4:
                continue
            yield line[0].lower()
            yield line[1].lower()
    with open('india_state_centres.txt', 'r') as f:
        for line in map(lambda x:x.strip().split(' '), f.readlines()):
            for word in line:
                word = word.strip()
                if word:
                    yield word.lower()

def get_good_followers(followers, locations, min_tweets):
    fewtweets = 0; nolocation = 0; badlocation = 0; accepted = 0; protected = 0

    for follower in followers:
        good_location = False
        if follower['statuses_count'] < min_tweets:
            print 'Skipping "%s" because he/she/it has only %d tweets' % (
                    follower['screen_name'], follower['statuses_count'])
            fewtweets += 1
            continue
        if not follower['location']:
            print 'Skipping "%s" because he has no location' % (
                    follower['screen_name'])
            nolocation += 1
            continue
        if follower['protected']:
            print 'Skipping "%s" because he is protected' % (
                    follower['screen_name'])
            protected += 1
            continue
        for location_part in re.split('[ ,]+', re.sub(r'[^a-zA-Z, ]', '',
                follower['location']).strip()):
            if location_part.lower() in locations:
                good_location = True
                break
        if good_location:
            accepted += 1
            yield follower
        else:
            badlocation += 1
            print 'Skipping "%s" because his location is ' \
                    '"%s", and I do not have that in my list' % (
                            follower['screen_name'], follower['location'])

    print
    print 'Stats: '
    for str, val in (('Bad location', badlocation),
                     ('No location', nolocation),
                     ('Too few tweets', fewtweets),
                     ('Accepted', accepted),
                     ('Protected', protected)):
        print '\t%s: %d (%.02f%%)' % (str, val, val*100./len(followers))

def check_clock(last_time):
    elapsed_time = (datetime.now() - last_time).seconds
    if elapsed_time < RATE_LIMIT_WINDOW:
        print 'Sleeping for %s seconds...' % (RATE_LIMIT_WINDOW - elapsed_time)
        sleep(RATE_LIMIT_WINDOW - elapsed_time)

def get_followers(twitter):
    locations = set(get_all_locations_in_india())
    
    num_followers = min(MAX_FOLLOWERS, twitter.show_user(screen_name=root)['followers_count'])
    
    next_cursor = -1; num_requests = 0; users_downloaded = 0; page_number = 1

    last_time = datetime.now()
    time_start = datetime.now()

    good_followers = []

    while users_downloaded < num_followers:
        print 'Downloading followers page %d for %s' % (page_number, root)
        try:
            response = twitter.get_followers_list(screen_name=root, count=FOLLOWER_BATCH_SIZE, cursor=next_cursor)
        except:
            continue
        followers = response['users']
        good_followers.extend((list(get_good_followers(followers, locations, MIN_TWEETS))))
        num_requests += 1
        if num_requests == FOLLOWER_RATE_LIMIT:
            check_clock(last_time)
            last_time = datetime.now()
            num_requests = 1
        next_cursor = response['next_cursor']
        users_downloaded += FOLLOWER_BATCH_SIZE
        page_number += 1

    f_followers = open('%s_good_followers_of.pickle'%(root), 'wb')
    pickle.dump(good_followers, f_followers)
    f_followers.close()

    duration = (datetime.now() - time_start).seconds
    print 'Number of good followers listed %s in %s seconds' % (len(good_followers), duration)

def get_twitter_data(twitter):
    f_followers = open('%s_good_followers_of.pickle'%(root), 'rb')
    followers = pickle.load(f_followers)
    f_followers.close()
    
    num_requests = 0; file_count = 1
    
    last_time = datetime.now()
    time_start = datetime.now()

    tweets = []
    
    for follower in followers:
        num_tweets = min(follower['statuses_count'], MAX_TWEETS)
        print 'Collecting %s tweets from %s' % (num_tweets, follower['screen_name'])
        max_tweet_id = 0; tweets_collected = 0
        
        while tweets_collected < num_tweets:
            new_tweets = []
            try:
                if(max_tweet_id == 0):
                    new_tweets = twitter.get_user_timeline(screen_name=follower['screen_name'], count=TWEET_BATCH_SIZE)
                else:
                    new_tweets = twitter.get_user_timeline(screen_name=follower['screen_name'], max_id=max_tweet_id, count=TWEET_BATCH_SIZE)
                tweets_collected += TWEET_BATCH_SIZE
            except TwythonRateLimitError:
                continue
            except TwythonError:
                continue
            num_requests += 1
            if num_requests == TWEET_RATE_LIMIT:
                check_clock(last_time)
                last_time = datetime.now()
                num_requests = 1
            for tweet in new_tweets:
                if max_tweet_id == 0 or max_tweet_id > int(tweet['id']):
                    max_tweet_id = int(tweet['id'])
            tweets.extend(new_tweets)

    f_tweets = open('%s_tweets.pickle'%(root), 'wb')
    pickle.dump(tweets, f_tweets)
    f_tweets.close()

    duration = (datetime.now() - time_start).seconds
    print 'Number of tweets collected %s in %s seconds' % (len(tweets), duration)
    
def main():
    global root
    if sys.argv > 1:
        root = sys.argv[1]
        APP_KEY = sys.argv[2]
        APP_SECRET = sys.argv[3]

    twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
    ACCESS_TOKEN = twitter.obtain_access_token()
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    
    get_followers(twitter)
    #get_twitter_data(twitter)
    
if __name__ == '__main__':
    main()
