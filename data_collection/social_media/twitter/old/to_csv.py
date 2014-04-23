'''
Author:
    Stefan Mihaila <stefan.mihaila@epfl.ch>
'''

import pickle
import csv
import glob
import sys

columns = ['user->id', 'meta->county', 'meta->city', 'meta->lat', 'meta->lng',
    'created_at', 'id', 'favorite_count', 'favorited', 'coordinates', 'lang',
    'place->place_type', 'retweet_count', 'retweeted', 'text']


def get_column(d, col):
    col = col.split('->')
    for c in col:
        if not isinstance(d,dict) or c not in d:
            return None
        d = d[c]
    return d

def get_tweets(fn='../../data_collection/twitter/tweets.pickle'):
    tweets = []
    with open(fn, 'rb') as f:
        while True:
            try:
                new_tweets = pickle.load(f)
                tweets += new_tweets
                #print 'loaded',len(new_tweets),'tweets'
            except:
                break
    return tweets

def main():
    if len(sys.argv) > 1:
        tweets = get_tweets(sys.argv[1])
    else:
        tweets = get_tweets()

    if not isinstance(tweets[0], dict):
        columns = None

    if len(sys.argv) > 2:
        if sys.argv[2] == 'all':
            columns = list(tweets[0].iterkeys())
        elif sys.argv[2] == 'nohead':
            columns = None
        elif sys.argv[2] == '-':
            pass
        else: 
            columns = sys.argv[2].split(',')

    outfile = sys.argv[3] if len(sys.argv) > 3 else 'tweets.csv'

    columns_written = False
    with open(outfile, 'w+') as f:
        f = csv.writer(f, quoting=csv.QUOTE_ALL)
        for t in tweets:
            if columns:
                f.writerow(map(lambda c:c.split('->')[-1], columns))
            if isinstance(t, dict):
                f.writerow(map(lambda c:unicode(get_column(t,
                    c)).encode('unicode-escape'), columns))
            else:
                f.writerow(map(lambda c:unicode(c).encode('unicode-escape'),
                    t))

if __name__ == '__main__':
    main()
