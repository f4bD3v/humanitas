import nltk
from sets import Set

# filters retweets & duplicates and returns tokenized tweets

def contains_words(to_check, tweet):
    for word in to_check:
        if (word in tweet):
            return True
    return False

# currently not used, because retweet check seems to
# remove more duplicates (maybe combination)
def is_duplicate(tweet):
    if(tweet in is_duplicate.tweets):
        return True
    else:
        is_duplicate.tweets.append(tweet)
        return False

def process_tweets(tweets):
    # init for is_duplicate
    # is_duplicate.tweets = []
    for t in tweets:
        tokens = nltk.word_tokenize(t['text'])
        tokens = map(lambda x: x.replace('.', ''), tokens)
        tokens = filter(lambda x: not x in
                ['?', ';', ':', '@', '#', ',', '!', 'a', '', 'to'],
                tokens)

        is_retweet = 'retweeted_status' in t

        features = tokens
        #features = [t['text'], t['favorite_count'], t['retweet_count']]

        if not is_retweet: #and (
        # not is_duplicate(t['text']) and (
        # contains_words(['meal', 'food'],
        # tokens)):
        #   print features
            yield features
