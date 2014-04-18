import argparse
import tarchunk
import json
from numba import jit

from multiprocessing import Process, Queue

parser = argparse.ArgumentParser( description="Filter and categorize tweets.")
parser.add_argument('outdir', metavar="OUTDIR", nargs='1', help="output directory")
parser.add_argument('files', metavar="TARFILE", nargs='+', help="tarfiles to unpack and filter to adequate size")

args = parser.parse_args()

count = 0;
path = "words/"

@jit
def alltweets():
    for tf in args.files:
        yield from tarchunk.open(tf)


def get_words(fn):
    word_set = set()

    with open(path + fn, 'r') as f:
       words = map(str.strip.lower, f.readlines())
       word_set.update(filter(bool, words))

    return word_set

@jit
def contains_words(to_check, tweet):
    for word in to_check:
        if (word in tweet):
            return True
    return False

@jit
def in_rect(p, r):
    return p[0] <= r[1][0] and p[0] => r[0][0] and
    p[1] <= r[1][1] and p[1] => r[0][1] 

#@jit
#def coords_in(country, coords):
#    return 'coordinates' in coords and
#           any(map(lambda x: in_rect(coords['coordinates'], x), country))
#           #in_rect(coords['coordinates'], country)

#india_coord = [((33, 68), (8, 89)), ((37, 73), (32, 80))]
#indo_coord = [((5, 95), (-10, 141))]

@jit
def coords_in_india(coords):
    return 'coordinates' in coords and
           in_rect(coords['coordinates'], ((33, 68), (8, 89))) and
           in_rect(coords['coordinates'], ((37, 73), (32, 80)))

@jit
def coords_in_indo(coords):
    return 'coordinates' in coords and
            #coords for indonisia have been switched
           in_rect(coords['coordinates'], ((-10, 95), (5, 141)))


@jit
def place_in(country, place):
    return 'country_code' in place and place['country_code'] == country

india_code = 'IN'
indo_code = 'ID'

food_words_india = get_words('food-words-india.txt')
predictor_words_india = get_words('predictor-words-india.txt')
region_words_india = get_words('region-words-india.txt')

food_words_indo = get_words('food-words-indo.txt')
predictor_words_indo = get_words('predictor-words-indo.txt')
region_words_indo = get_words('region-words-indo.txt')

#filtered tweets with indian coordinates
f_india_coords = open(args.outdir + "tweets_india_coords.json", 'w')
#filtered tweets mentioning a region
f_india_regions = open(args.outdir + "tweets_india_regions.json", 'w')
#filtered tweets mentioning a region
f_india_places = open(args.outdir + "tweets_india_places.json", 'w')


#filtered tweets with indonesian coordinates
f_indo_coords = open(args.outdir + "tweets_indo_coords.json", 'w')
#filtered tweets mentioning a region
f_indo_regions = open(args.outdir + "tweets_indo_regions.json", 'w')
#filtered tweets mentioning a region
f_indo_places = open(args.outdir + "tweets_indo_places.json", 'w')

#tweets filtered with indian words
f_india_unknown = open(args.outdir + "tweets_india_unknown.json", 'w')
#tweets filtered with indonesian words
f_indo_unknown = open(args.outdir + "tweets_indo_unknown.json", 'w')

@jit
def process_tweet(tweet):
    tweet_text = tweet['text'].lower()
    if(contains_words(food_words_india, tweet_text) and
      contains_words(predictor_words_india, tweet_text)):

       if('coordinates' in tweet and coords_in(india_coord, tweet['coordinates'])):
          f_india_coords.write(tweet)
       elif('place' in tweet and place_in(india_code, tweet['place'])):
          f_india_places.write(tweet)
       elif(contains_words(region_words_india, tweet_text):
          f_india_regions.write(tweet)
       else:
          f_india_unknown.write(tweet)

    elif(contains_words(food_words_indo, tweet_text) and
      contains_words(predictor_words_indo, tweet_text):

       if('coordinates' in tweet and coords_in(indo_coord, tweet['coordinates'])):
          f_indo_coords.write(tweet)
       elif('place' in tweet and place_in(indo_code, tweet['place'])):
          f_indo_places.write(tweet)
       elif(contains_words(region_words_indo, tweet_text)):
          f_indo_regions.write(tweet)
       else:
          f_indo_unknown.write(tweet)

@jit
def main():
	for tweet in alltweets():
	    if('text' in tweet and not 'retweeted_status' in tweet):
		#p = Process(target=process_tweet, args=(tweet,q,))
		#p.start()
		process_tweet(tweet)

	    if(count % 10000 == 0)
		print(count)

	    count += 1


main()

f_india_coords.close()
f_india_regions.close()
f_india_places.close()

f_indo_coords.close()
f_indo_regions.close()
f_indo_places.close()

f_india_unknown.close()
f_indo_unknown.close()

