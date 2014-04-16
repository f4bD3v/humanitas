from twython import Twython, TwythonError, TwythonRateLimitError
from datetime import datetime
from time import sleep
from sys import maxint
import re
import pickle
import csv

APP_KEY = 'aylam3pBvHkhOUmycOWw'
APP_SECRET = 'uXAuZwGX8FUno0P54gdIlGnkijhkY56lVFxRwgjgI'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

root = "KareenaOnline" #'pythoncentral'#
RATE_LIMIT_WINDOW = 15 * 60
TWEET_BATCH_SIZE = 200
FOLLOWER_RATE_LIMIT = 30
FOLLOWER_BATCH_SIZE = 200
TWEET_RATE_LIMIT = 300
MIN_TWEETS = 50
MAX_TWEETS = 3200
MAX_TWEETS_PER_FILE = 100000

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

def get_followers():
    f_followers = open('good_followers_of.csv', 'wb')
    csv_writer = csv.writer(f_followers)
    csv_writer.writerow(['screen_name','statuses_count','location'])
    
    locations = set(get_all_locations_in_india())
    num_followers = 20000 #twitter.show_user(screen_name=root)['followers_count']

    next_cursor = -1; num_requests = 0; users_downloaded = 0; page_number = 1; num_good_followers = 0

    last_time = datetime.now()
    time_start = datetime.now()

    while users_downloaded < num_followers:
        print 'Downloading followers page %d for %s' % (page_number, root)
        try:
            response = twitter.get_followers_list(screen_name=root, count=FOLLOWER_BATCH_SIZE, cursor=next_cursor)
        except:
            continue
        followers = response['users']
        good_followers = (list(get_good_followers(followers, locations, MIN_TWEETS)))
        num_good_followers += len(good_followers)
        for follower in good_followers:
            csv_writer.writerow([follower['screen_name'].encode('utf8'), follower['statuses_count'], follower['location'].encode('utf8')])
        num_requests += 1
        if num_requests == FOLLOWER_RATE_LIMIT:
            check_clock(last_time)
            last_time = datetime.now()
            num_requests = 1                          
        next_cursor = response['next_cursor']
        users_downloaded += FOLLOWER_BATCH_SIZE
        page_number += 1
        
    f_followers.close()

    duration = (datetime.now() - time_start).seconds
    print 'Number of good followers listed %s in %s seconds' % (num_good_followers, duration)

def get_twitter_data():
    f_followers = open('good_followers_of.csv', 'rb')
    follower_reader = csv.reader(f_followers)
    next(follower_reader)
    
    f_tweets = open('tweets%s.csv'%(1), 'wb')
    tweet_writer = csv.writer(f_tweets)
    tweet_writer.writerow(['created_at','screen_name','text'])
    
    num_requests = 0; tweet_count = 0; file_count = 1
    last_time = datetime.now()

    time_start = datetime.now()
    
    for follower in follower_reader:
        screen_name = follower[0]; statuses_count = int(follower[1]); location = follower[2]
        num_tweets = min(statuses_count, MAX_TWEETS)
        print 'Collecting %s tweets from %s' % (num_tweets, screen_name)
        max_tweet_id = 0; tweets_collected = 0; tweets = []
        
        while tweets_collected < num_tweets:
            try:
                if(max_tweet_id == 0):
                    tweets = twitter.get_user_timeline(screen_name=screen_name, count=TWEET_BATCH_SIZE)
                else:
                    tweets.extend(twitter.get_user_timeline(screen_name=screen_name,
                                                        max_id=max_tweet_id, count=TWEET_BATCH_SIZE))
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
            for tweet in tweets:                   
                if max_tweet_id == 0 or max_tweet_id > int(tweet['id']):
                    max_tweet_id = int(tweet['id'])
        for tweet in tweets:
            tweet_writer.writerow([tweet['created_at'].encode('utf8'), tweet['user']['screen_name'].encode('utf8'), tweet['text'].encode('utf8')])
            tweet_count += 1
            if(tweet_count%MAX_TWEETS_PER_FILE == 0):
                f_tweets.close()
                file_count += 1
                f_tweets = open('tweets%s.csv'%(file_count), 'wb')
                tweet_writer = csv.writer(f_tweets)
                tweet_writer.writerow(['created_at','screen_name','text'])
    
    f_tweets.close()
    f_followers.close()

    duration = (datetime.now() - time_start).seconds    
    print 'Number of tweets collected %s in %s seconds' % (tweet_count, duration)
    
def main():
    get_followers()
    get_twitter_data()
    
if __name__ == '__main__':
    main()
