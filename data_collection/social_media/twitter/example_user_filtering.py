import re
from twython import Twython
import pickle


APP_KEY = 'pdSvpPsuBfT9R21ii6KPqw'
APP_SECRET = 'X1nyXfoLsYWeMhM01rRgwlskfmFPEo60mq5QUszBwo8'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

def get_followers_of(user, max_calls):
    ret = []
    cursor = -1
    for i in xrange(max_calls):
        print 'Downloading followers page %d for %s' % (i+1, user)
        response = twitter.get_followers_list(screen_name=user, 
                count=200, cursor=cursor)
        ret += response['users']
        if len(response['users']) < 200:
            break
        cursor = response['next_cursor']
    return ret

def get_all_locations_in_india():
    yield 'india'
    with open('cities-in-india.txt', 'r') as f:
        for line in map(lambda x:re.split(r'[\s\t]+', x), f.readlines()):
            if len(line) != 4:
                continue
            yield line[0].lower()
            yield line[1].lower()
    with open('india_state_centres.txt', 'r') as f:
        for line in map(lambda x:x.strip().split(' '), f.readlines()):
            for word in line:
                word = word.strip()
                if word:
                    yield word.lower()

def get_good_followers(followers, locations, min_tweets):
    # stats
    fewtweets = 0
    nolocation = 0
    badlocation = 0
    accepted = 0
    protected = 0

    for follower in followers:
        good_location = False
        if follower['statuses_count'] < min_tweets:
            print 'Skipping "%s" because he has only %d tweets' % (
                    follower['screen_name'], follower['statuses_count'])
            fewtweets += 1
            continue
        if not follower['location']:
            print 'Skipping "%s" because he has no location' % (
                    follower['screen_name'])
            nolocation += 1
            continue
        if follower['protected']:
            print 'Skipping "%s" because he is protected' % (
                    follower['screen_name'])
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
            print 'Skipping "%s" because his location is ' \
                    '"%s", and I do not have that in my list' % (
                            follower['screen_name'], follower['location'])

    print
    print 'Stats: '
    for str, val in (('Bad location', badlocation),
                     ('No location', nolocation),
                     ('Too few tweets', fewtweets),
                     ('Accepted', accepted),
                     ('Protected', protected)):
        print '\t%s: %d (%.02f%%)' % (str, val, val*100./len(followers))


def main():
    # example
    locations = set(get_all_locations_in_india())

    # the api calls are saved in this example
    try:
        with open('followers_of.pickle', 'rb') as f:
            followers = pickle.load(f)
            print 'Loaded cached followers list from followers_of.pickle (' \
                    'delete the file if you want me to contact the api)'
    except:
        with open('followers_of.pickle', 'w+b') as f:
            followers = get_followers_of('BeingSalmanKhan', 20)
            pickle.dump(followers, f)

    followers = list(get_good_followers(followers, locations, 100))
    print
    for f in followers:
        print 'Found "%s" with %d tweets from %s' % (f['screen_name'],
                f['statuses_count'], f['location'])

    print ' '.join(map(lambda x:x['screen_name'], followers))

if __name__ == '__main__':
    main()
