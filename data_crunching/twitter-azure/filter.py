#!/usr/bin/env python3

import argparse
from chunked import chunked
#import subprocess
import tarchunk
import json

parser = argparse.ArgumentParser( description="Resize tar chunks and send them to some command")
parser.add_argument('-s', '--size', metavar="N", help='chunk size in number of tweets', default=1000000);
#parser.add_argument('command', metavar="COMMAND", help='command to invoke to process chunks. Chunk number will be passed as argument, and data provided on stdin.')
parser.add_argument('files', metavar="TARFILE", nargs='+', help="tarfiles to unpack and repack at the adequate size")

args = parser.parse_args()

count = 0;
chunk = 0;

def alltweets():
    for tf in args.files:
        yield from tarchunk.open(tf)


def get_words():
    predictor_words = set()
    food_words = set()

    # XXX `apple' used to be on the list but it just gives too much bad data
    for fn, var in (('predictor-words.txt', predictor_words),
                    ('food-words.txt', food_words)):
        with open(fn, 'r') as f:
            words = map(str.strip, f.readlines())
            var.update(filter(bool, words))

    return predictor_words, food_words

def contains_words(to_check, tweet):
    for word in to_check:
        if (word in tweet):
            return True
    return False

predictor_words, food_words = get_words()

#decoder = json.JSONDecoder()
count = 0
for chunk in chunked(alltweets(), size=args.size):
    #p = subprocess.Popen([args.command, str(count).zfill(5)],
    #                     stdin=subprocess.PIPE, )
    #f = open("chuck_" + count, "w+")

    for line in chunk:
        #print(tweet)
        #tweet = decoder.decode(line)
        if('text' in line and not 'retweeted_status' in line):
           tweet = line['text'].lower()
           if(contains_words(predictor_words, tweet) and
              contains_words(food_words, tweet)):
              print(tweet)
        #p.stdin.write(line)

    #p.stdin.close()
    #p.wait()

    count += 1
