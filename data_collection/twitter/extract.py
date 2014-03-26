from twython import Twython
import pprint
import pickle
import logging
import sys
import re

'''
Author:
    Stefan Mihaila <stefan.mihaila@epfl.ch>
'''

APP_KEY = 'pdSvpPsuBfT9R21ii6KPqw'
APP_SECRET = 'X1nyXfoLsYWeMhM01rRgwlskfmFPEo60mq5QUszBwo8'
#ACCESS_TOKEN = '49012069-KcdSrQMgmTqZpq1wMgc9wjV7z6BHmZwn45iCTG2bo'


def get_words():
    predictor_words = set()
    food_words = set()

    for fn, var in (('predictor-words.txt', predictor_words),
                    ('food-words.txt', food_words)):
        with open(fn, 'r') as f:
            words = map(str.strip, f.readlines())
            var.update(filter(bool, words))

    return predictor_words, food_words

def get_coords():
    with open('india-coords.txt', 'r') as f:
        return map(lambda x:map(float,x.split(',')), f.readlines())

def make_twitter_query(predictor_words, food_words):
    lhs = ' OR '.join(predictor_words)
    # query fails with >18
    rhs = ' OR '.join(list(food_words)[0:10])
    return '(%s) (%s)' % (lhs, rhs)

def download_geolocated_tweets(twitter, lat, lng, query, resume_at=None,
                               limit=5000):
    statuses = []
    extra = {}
    if resume_at:
        extra['max_id'] = resume_at

    #query = 'test'
    while len(statuses) < limit:
        result = twitter.search(q=query, lang='en', 
                geocode='%f,%f,400km'%(lat,lng), 
                count=100, **extra)
        statuses += result['statuses']
        logging.info('Query (id<=%s) for (%f,%f): %d results',
                extra.get('max_id', 'NA'), lat, lng,
                len(result['statuses']))
        if len(result['statuses']) < 100:
            extra['max_id'] = 0
            break

        extra['max_id'] = int(
            re.search('max_id=(\d+)',
                result['search_metadata']['next_results']).group(1)
        )

    #print pprint.pprint(result)
    logging.info('Got %d tweets for (%f,%f)', len(statuses), lat, lng)
    return statuses, extra['max_id']



def main():
    logging.basicConfig(level=logging.INFO)

    predictor_words, food_words = get_words()
    query = make_twitter_query(predictor_words, food_words)
    coords = get_coords()

    twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
    access_token = twitter.obtain_access_token()
    twitter = Twython(APP_KEY, access_token=access_token)

    logging.info('Loading previous state')

    tweets = []
    
    try:
        with open('state.pickle', 'r+b') as f:
            state = pickle.load(f)
    except:
        state = {}

    logging.info('Downloading new tweets')
    for lat, lng in coords:
        try:
            if (lat, lng) not in state:
                state[(lat, lng)] = None
            elif state[(lat, lng)] == 0:
                logging.info('Already covered all of (%f, %f), moving on',
                        lat, lng)
                continue
            new_tweets, resume_at = \
                    download_geolocated_tweets(twitter, lat, lng, query,
                            state[(lat, lng)])
            tweets += new_tweets
            state[(lat, lng)] = resume_at
        except Exception, e:
            logging.exception(e)

    logging.info('Saving tweets and state')

    if tweets:
        with open('tweets.pickle', 'a+b') as f:
            pickle.dump(tweets, f, protocol=pickle.HIGHEST_PROTOCOL)

    with open('state.pickle', 'w+b') as f:
        pickle.dump(state, f, protocol=pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    main()
