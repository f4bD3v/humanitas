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
