import pickle
import glob
import sys
import os
import csv

sys.path += ['../../data_collection/twitter']
from to_csv import get_column, get_tweets

header = ['Text', 'Favorited count', 'Retweeted count',
          'Contains word meal', 'Contains word food']

def process_tweets(tweets):
    for t in tweets:
        # insert your NLP and other techniques for processing tweets here
        # for the keys of the dictionary `t', see
        # https://dev.twitter.com/docs/platform-objects/tweets
        contains_word_meal = 'meal' in t['text']
        contains_word_food = 'food' in t['text']
        features = [t['text'], t['favorite_count'], t['retweet_count'],
                contains_word_food, contains_word_meal]
        yield features

def main():
    cwd = os.getcwd()
    os.chdir('../../data_collection/twitter')
    tweets = get_tweets()
    os.chdir(cwd)

    with open('twitter-features.csv', 'w+') as f:
        f = csv.writer(f, quoting=csv.QUOTE_ALL)
        f.writerow(header)
        for row in process_tweets(tweets):
            f.writerow(map(lambda s:unicode(s).encode('unicode-escape'), row))

if __name__ == '__main__':
    main()
