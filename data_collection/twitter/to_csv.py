'''
Author:
    Stefan Mihaila <stefan.mihaila@epfl.ch>
'''

import pickle
import csv
import glob

columns = ['user->id', 'created_at', 'id', 'favorite_count', 'favorited', 'coordinates', 'lang',
        'place->place_type', 'retweet_count', 'retweeted', 'text']

def get_column(d, col):
    col = col.split('->')
    for c in col:
        if not isinstance(d,dict) or c not in d:
            return None
        d = d[c]
    return d

def get_tweets():
    tweets = []
    with open('tweets.pickle', 'rb') as f:
        while True:
            try:
                tweets += pickle.load(f)
            except:
                break
    return tweets

def main():
    tweets = get_tweets()
    with open('tweets.csv', 'w+') as f:
        f = csv.writer(f)
        f.writerow(columns)
        for t in tweets:
            f.writerow(map(lambda c:unicode(get_column(t,
                c)).encode('unicode-escape'), columns))

if __name__ == '__main__':
    main()
