from twython import Twython, TwythonError, TwythonRateLimitError, TwythonAuthError
from datetime import datetime
from time import sleep
from sys import maxint
import re
import csv
import sys
import pickle
import traceback

RATE_LIMIT_WINDOW = 15 * 60
WAIT_BETWEEN_AUTH = 10 * 60
BUFFER = 5
TWEET_RATE_LIMIT = 300
TWEET_BATCH_SIZE = 200
FOLLOWER_RATE_LIMIT = 30
FOLLOWER_BATCH_SIZE = 200
MIN_TWEETS = 50
MAX_TWEETS = 3200
MAX_FOLLOWERS = 2000000
MAX_TWEETS_PER_FILE = 15000
MAX_USERS_PER_FILE = 5000

input_folder = "tweet_inputs/"
output_folder = "tweet_tmp_store/"
users_folder = "users/"

def get_all_locations_in_india():
    yield 'india'
    with open(input_folder + 'cities-in-india.txt', 'r') as f:
        for line in map(lambda x:re.split(r'[\s\t]+', x), f.readlines()):
            if len(line) != 4:
                continue
            yield line[0].lower()
            yield line[1].lower()
    with open(input_folder + 'india_state_centres.txt', 'r') as f:
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
##            print 'Skipping "%s" because he/she/it has only %d tweets' % (
##                    follower['screen_name'], follower['statuses_count'])
            fewtweets += 1
            continue
        if not follower['location']:
##            print 'Skipping "%s" because he has no location' % (
##                    follower['screen_name'])
            nolocation += 1
            continue
        if follower['protected']:
##            print 'Skipping "%s" because he is protected' % (
##                    follower['screen_name'])
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
##            print 'Skipping "%s" because his location is ' \
##                    '"%s", and I do not have that in my list' % (
##                            follower['screen_name'], follower['location'])

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
        write_log('Sleeping for %s seconds...\n' % (RATE_LIMIT_WINDOW - elapsed_time))
        sleep(RATE_LIMIT_WINDOW - elapsed_time)

def write_log(message):
    f_log = open("log.txt", 'a')
    f_log.write(message)
    f_log.close()

def data_dump(data, file_name):
    f = open(file_name, 'wb')
    pickle.dump(data, f)
    f.close()

def authenticate(APP_KEY, APP_SECRET):
    while True:
        write_log('Authenticating to Twitter...\n')
        try:
            twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
            ACCESS_TOKEN = twitter.obtain_access_token()
            ret = Twython(APP_KEY, access_token=ACCESS_TOKEN)
            write_log('Authentication successful\n')
            return ret
        except TwythonAuthError, e:
            traceback.print_exc()
            sleep(WAIT_BETWEEN_AUTH)

def get_followers(root, APP_KEY, APP_SECRET):
    twitter = authenticate(APP_KEY, APP_SECRET)

    locations = set(get_all_locations_in_india())
    num_followers = min(MAX_FOLLOWERS, twitter.show_user(screen_name=root)['followers_count'])
    next_cursor = -1; num_requests = 0; users_downloaded = 0; num_good_followers = 0; page_number = 1; file_count = 0

    last_time = datetime.now()
    time_start = datetime.now()

    good_followers = []

    while users_downloaded < num_followers:
        write_log('Downloading followers page %d for %s\n' % (page_number, root))
        try:
            response = twitter.get_followers_list(screen_name=root, count=FOLLOWER_BATCH_SIZE, cursor=next_cursor)            
            followers = response['users']
        except TwythonRateLimitError:
            write_log('Sleeping...\n')
            sleep(RATE_LIMIT_WINDOW)
            continue
        except TwythonError:
            continue
        except KeyError:
            continue

        size_good_followers = len(good_followers)
        good_followers.extend((list(get_good_followers(followers, locations, MIN_TWEETS))))
        num_good_followers += len(good_followers) - size_good_followers
        
        num_requests += 1
        if num_requests == FOLLOWER_RATE_LIMIT:
            check_clock(last_time)
            last_time = datetime.now()
            num_requests = 1
        
        next_cursor = response['next_cursor']
        page_number += 1
        users_downloaded += FOLLOWER_BATCH_SIZE

        if len(good_followers) >= MAX_USERS_PER_FILE:
            file_count += 1
            data_dump(good_followers, users_folder + '%s_%s.pickle'%(root, file_count))
            good_followers = []
        
        write_log(('%.02f%%\n')%(100.0 * users_downloaded / num_followers))
        write_log('%s good followers collected\n'%(num_good_followers))

    file_count += 1
    data_dump(good_followers, users_folder + '%s_%s.pickle'%(root, file_count))
    duration = (datetime.now() - time_start).seconds
    write_log('Number of good followers listed %s in %s seconds\n' % (num_good_followers, duration))

def get_twitter_data(root, APP_KEY, APP_SECRET):
    twitter = authenticate(APP_KEY, APP_SECRET)
    
    f_followers = open(input_folder + '%s.pickle'%(root), 'rb')
    followers = pickle.load(f_followers)
    f_followers.close()
    
    num_requests = 0; file_count = 1; total_tweets = 0; follower_number = 0
    last_time = datetime.now(); time_start = datetime.now(); log_time = datetime.now()
    tweets = []
    
    write_log('%s followers available\n'%(len(followers)))
    
    for follower in followers:
        num_tweets = min(follower['statuses_count'], MAX_TWEETS)
        write_log('Collecting %s tweets from %s\n'%(num_tweets, follower['screen_name']))
        max_tweet_id = 0; tweets_collected = 0
        
        while tweets_collected < num_tweets:
            new_tweets = []
            if num_requests == TWEET_RATE_LIMIT:
                check_clock(last_time)
                last_time = datetime.now()
                num_requests = 1
            try:
                num_requests += 1
                if max_tweet_id == 0:
                    new_tweets = twitter.get_user_timeline(screen_name=follower['screen_name'], count=TWEET_BATCH_SIZE)
                else:
                    new_tweets = twitter.get_user_timeline(screen_name=follower['screen_name'], max_id=max_tweet_id, count=TWEET_BATCH_SIZE)
                tweets_collected += TWEET_BATCH_SIZE
                total_tweets += len(new_tweets)
            except TwythonRateLimitError:
                write_log('Rate limit error - sleeping...\n')
                sleep(RATE_LIMIT_WINDOW)
                last_time = datetime.now()
                num_requests = 1
                continue
            except TwythonError:
                break
            for tweet in new_tweets:
                if max_tweet_id == 0 or max_tweet_id > int(tweet['id']):
                    max_tweet_id = int(tweet['id'])
            tweets.extend(new_tweets)
            
        if total_tweets >= file_count * MAX_TWEETS_PER_FILE:
            data_dump(tweets, output_folder + '%s_tweets_%s.pickle'%(root, file_count + 1000))
            file_count += 1
            tweets = []

        follower_number += 1
        
        write_log(('%s tweets collected\n')%(total_tweets))
        write_log(('%.02f%%\n')%(100.0 * follower_number / len(followers)))
        
    data_dump(tweets, output_folder + '%s_tweets_%s.pickle'%(root, file_count + 1000))
    duration = (datetime.now() - time_start).seconds
    write_log('Number of tweets collected %s in %s seconds\n' % (total_tweets, duration))
    
def main():
    APP_KEY = sys.argv[1]
    APP_SECRET = sys.argv[2]
    root = sys.argv[3]
    option = sys.argv[4]
        
    if option == 'users' or option == 'both':
        get_followers(root, APP_KEY, APP_SECRET)
    if option == 'tweets' or option == 'both':
        get_twitter_data(root, APP_KEY, APP_SECRET)
    
if __name__ == '__main__':
    main()
