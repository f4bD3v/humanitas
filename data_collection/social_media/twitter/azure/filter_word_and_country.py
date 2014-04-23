import argparse
import json
import bz2
import io
import tarfile
import sys

#from numba import jit, autojit

if sys.hexversion < 0x03030000:
    print("WARNING: this code is known to fail for python < 3.3", file=sys.stderr)

parser = argparse.ArgumentParser( description="Filter and categorize tweets.")
parser.add_argument('outdir', help="output directory")
parser.add_argument('files', metavar="TARFILE", nargs='+', help="tarfiles to unpack and filter to adequate size")

args = parser.parse_args()

path = "words/"

def open_tweets(tarname):
    tar = tarfile.open(tarname, mode='r|*')
    for tarinfo in tar:
        name = tarinfo.name
        try:   
            obj = tar.extractfile(tarinfo)
            if obj is None:
                continue

            for line in bz2.open(obj):
                yield (json.loads(line.decode('utf8')), line)
        except Exception as e:
            print("Failed on {0}: {1}".format(name, e))


##@jit
def alltweets():
    for tf in args.files:
        yield from open_tweets(tf)


def get_words(fn):
    word_set = set()

    with open(path + fn, 'r') as f:
       words = map(lambda x: str.lower(str.strip(x)), f.readlines())
       word_set.update(filter(bool, words))

    return word_set

#@jit
def contains_words(to_check, tweet):
    for word in tweet:
        if (word in to_check):
            return True
    return False

#@jit
def in_rect(p, r):
    return (p[0] >= r[0][0] and p[0] <= r[1][0]) and (
           p[1] <= r[0][1] and p[1] >= r[1][1])

#@jit
#def coords_in(country, coords):
#    return 'coordinates' in coords and
#           any(map(lambda x: in_rect(coords['coordinates'], x), country))
#           #in_rect(coords['coordinates'], country)

#lati, long
#india_coord = [((33, 68), (8, 89)), ((37, 73), (32, 80))]
#indo_coord = [((5, 95), (-10, 141))]

#@jit
def coords_in_india(coords):
    return 'coordinates' in coords and (
           in_rect(coords['coordinates'], ((68.0, 33.0), (89.0, 8.0))) and
           in_rect(coords['coordinates'], ((73.0, 37.0), (80.0, 32.0))) )

#@jit
def coords_in_indo(coords):
    return 'coordinates' in coords and (
           in_rect(coords['coordinates'], ((95.0, 5.0), (141.0, -10.0))) )


#@jit
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

f_mode = 'wb'
outdir = args.outdir + "/"

## filtered tweets categorized

#indian coordinates
f_india_coords = open(outdir + "tweets_india_coords.json", f_mode)
#mentioning a region or city in india
f_india_regions = open(outdir + "tweets_india_regions.json", f_mode)
#place attribute set to india
f_india_places = open(outdir + "tweets_india_places.json", f_mode)
#user location set to india or a city in india
f_india_userloc = open(outdir + "tweets_india_userloc.json", f_mode)

#indonesian coordinates
f_indo_coords = open(outdir + "tweets_indo_coords.json", f_mode)
#mentioning a region or city in indonesia
f_indo_regions = open(outdir + "tweets_indo_regions.json", f_mode)
#place attribute set to indonesia
f_indo_places = open(outdir + "tweets_indo_places.json", f_mode)
#user location set to india or a city in indonesia
f_indo_userloc = open(outdir + "tweets_indo_userloc.json", f_mode)

#indian words + unknown location
f_india_unknown = open(outdir + "tweets_india_unknown.json", f_mode)
#indonesian words + unknown location
f_indo_unknown = open(outdir + "tweets_indo_unknown.json", f_mode)

#@jit
def process_tweet(tweet, line):
    tweet_text = tweet['text'].lower().split()
    if(contains_words(food_words_india, tweet_text) and
      contains_words(predictor_words_india, tweet_text)):

       if('coordinates' in tweet and tweet['coordinates'] is not None):
          if(coords_in_india(tweet['coordinates'])):
              f_india_coords.write(line)
          elif(coords_in_indo(tweet['coordinates'])):
              f_indo_coords.write(line)
       elif('place' in tweet and tweet['place'] is not None):
          if(place_in(india_code, tweet['place'])):
              f_india_places.write(line)
          elif(place_in(indo_code, tweet['place'])):
              f_indo_places.write(line)

       elif(contains_words(region_words_india, tweet_text) and
            not contains_words(['indiana'], tweet_text)):
          f_india_regions.write(line)
       elif('user' in tweet and tweet['user'] is not None and (
            'location' in tweet['user'] and
            tweet['user']['location'] is not None and
            contains_words(tweet['user']['location'].lower(), region_words_india) and
            not contains_words(tweet['user']['location'].lower(), ['indiana']))):
           f_india_userloc.write(line)
       else:
          f_india_unknown.write(line)

    elif (contains_words(food_words_indo, tweet_text)) and (
      contains_words(predictor_words_indo, tweet_text)):

       if('coordinates' in tweet and tweet['coordinates'] is not None):
          if(coords_in_indo(tweet['coordinates'])):
              f_indo_coords.write(line)
       elif('place' in tweet and tweet['place'] is not None):
          if(place_in(indo_code, tweet['place'])):
              f_indo_places.write(line)

       elif(contains_words(region_words_indo, tweet_text)):
          f_indo_regions.write(line)
       elif('user' in tweet and tweet['user'] is not None and (
            'location' in tweet['user'] and
            tweet['user']['location'] is not None and
            contains_words(tweet['user']['location'].lower(), region_words_indo))):
           f_indo_userloc.write(line)
       else:
          f_indo_unknown.write(line)

#@autojit
def main():
    #count = 0
    for (tweet, line) in alltweets():
        #print(tweet)
        #print("test\n")
        if('text' in tweet and 'retweeted_status' not in tweet):
            #p = Process(target=process_tweet, args=(tweet,q,))
            #p.start()
            process_tweet(tweet, line)

        #if(count % 10000 == 0):
        #    print(count)

        #count += 1


main()

f_india_coords.close()
f_india_regions.close()
f_india_places.close()
f_india_userloc.close()

f_indo_coords.close()
f_indo_regions.close()
f_indo_places.close()
f_indo_userloc.close()

f_india_unknown.close()
f_indo_unknown.close()

