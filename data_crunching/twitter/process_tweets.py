import pickle
import glob
import sys
import os
import csv

sys.path += ['../../data_collection/twitter']
from to_csv import get_column, get_tweets


def usage():
    print '''python %s <filter1,filter2,..,filterN> [input file] [output file]'
    Defaults: input file = ../data_collection/twitter/tweets.pickle
              output file = filter_results/tweets-<filtername>.pickle
    To learn how to create a filter, see filters/example.py''' % sys.argv[0]
    

def main():
    if len(sys.argv) < 2:
        usage()
        sys.exit(-1)
    filters = sys.argv[1].split(',')
    input_file = sys.argv[2] if len(sys.argv) > 2 else \
            '../../data_collection/twitter/tweets.pickle'
    output_file = sys.argv[3] if len(sys.argv) > 3 else \
            ('filter_results/tweets-%s.pickle' % '-'.join(filters))
    tweets = get_tweets(input_file)


    for f in filters:
         tweets = __import__('filters.' + f,
                 fromlist=['*']).process_tweets(tweets)

    with open(output_file, 'w+b') as f:
        pickle.dump(list(tweets), f, protocol=pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
