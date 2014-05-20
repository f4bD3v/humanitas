#---------------------------------
#Joseph Boyd - joseph.boyd@epfl.ch
#---------------------------------

from datetime import datetime
from twython import Twython
from sys import getsizeof

APP_KEY = 'aylam3pBvHkhOUmycOWw'
APP_SECRET = 'uXAuZwGX8FUno0P54gdIlGnkijhkY56lVFxRwgjgI'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

#Set root account:
root = "BeingSalmanKhan"
user_timeline = twitter.get_user_timeline(screen_name=root)

#Print tweets from @[root]:
for tweet in user_timeline:
    print(tweet['text'])

follower_ids = twitter.get_followers_ids(screen_name=root, count=5000)

f = open('tweets.txt', 'w')
user_count = 0
tweet_count = 0
private_count = 0

start_time = datetime.now()

#Collect tweets for each follower of [root]:
for follower in follower_ids['ids']:
    #try:
    #    print twitter.get_geo_info(user_id=follower)
    #except:
    #    print 'Geo info private'
    try:
        follower_timeline = twitter.get_user_timeline(user_id=follower)
        user_count += 1
        for tweet in follower_timeline:
            f.write(tweet['text'].encode('utf8') + '\n')
            tweet_count += 1
        print 'Tweet data collected'
    except:
        output = twitter.lookup_user(user_id=follower)
        print output[0]['screen_name'], 'Tweet data private'
        private_count += 1

end_time = datetime.now()

print str(tweet_count) + ' tweets from ' + str(user_count) + ' users collected in ' + str((end_time - start_time).seconds) + ' seconds.'

f.close()
