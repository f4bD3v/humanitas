from operator import itemgetter

#quick and dirty word count
#needs as input a list of tokenized tweets (e.g. words.py)

def process_tweets(tweets):
    word_counts = {}
    for t in tweets:
        for word in t:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
    
    wc = sorted(word_counts.items(), key=itemgetter(1))
    print wc
    return wc
    
    #for word in word_counts:    
    #    yield (word, word_counts[word])
