'''
duynguyen
'''

'''
Prerequisites:
- Install mongodb
- pip install pymongo
'''

import pickle
import sys

from pymongo import MongoClient

def get_tweets(fn='data_collection/twitter/tweets.pickle'):
    tweets = []
    with open(fn, 'rb') as f:
        while True:
            try:
                new_tweets = pickle.load(f)
                tweets += new_tweets
            except:
                break
    return tweets

def main():
    if len(sys.argv) > 1:
        tweets = get_tweets(sys.argv[1])
    else:
        tweets = get_tweets()

    client = MongoClient()
    db = client.humanitas
    collection = db.tweets
    for t in tweets:
    	collection.insert(t)

if __name__ == '__main__':
    main()
