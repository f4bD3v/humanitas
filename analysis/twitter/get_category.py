#!/usr/bin/env python2

import sys
import pylru

# Install nltk: 'sudo pip install -U pyyaml nltk'
from nltk.stem.lancaster import LancasterStemmer 

# Import predictor words (predictors_dict)
sys.path.append('keywords')
import predictors

# predictors_dict = 
#       { 'predict': { 'dec': ['decline'], 'inc': ['increase'] },
#         'price': { 'high': ['high'], 'low': ['low'] },
#         ... }
predictors_dict = predictors.predictors_dict

SPELLCHECKER_ENABLED = True
STEMMING_CACHING = True

negative_forms = ['not', 'no', 'non', 'nothing',
                  "don't", "dont", "doesn't", "doesnt",     # Present
                  "aren't", "arent", "a'int", "aint",
                  "isn't", "isnt",
                  "didn't", "didnt", "haven't", "havent",   # Past
                  "hasn't", "hasnt", "hadn't", "hadnt",
                  "weren't", "werent", "wasn't", "wasnt",
                  "wouldn't", "wouldnt",
                  "won't", "wont", "shan't", "shant",       # Future
                 ]

# Reverse index, for ex {'decline' : ('predict', 'dec')}
c_stems = {}
compl_pred_cats = {}
st = LancasterStemmer()
cache = pylru.lrucache(10000)

# Predictor categories
pred_categories = []

# Additional categories
additional_categories = []


def extend_categories(l):
    additional_categories.extend(l) 

# 1. Build reverse index for existing categories
def init_reverse_index():
    for dict_name in predictors_dict:
        category_dict = predictors_dict[dict_name]
        cats = category_dict.keys()
        for catkey in cats:
            for catval in cats:
                if catkey is not catval:
                    compl_pred_cats[catkey]=catval
        for cname in category_dict:
            pred_categories.append(str(dict_name)+'_'+str(cname))
            word_list = category_dict[cname]
            for word in word_list:
                stem = st.stem(word)
                c_stems[stem] = (dict_name, cname)
    # Add negative forms
    for word in negative_forms:
        c_stems[word] = ('negation', None)

# cache: word -> stem


def lookup_stem_sets(w):
    stem = get_stem(w)
    if stem in c_stems:
        return c_stems[stem]
    else:
        return None

if STEMMING_CACHING:
    def get_stem(w):
        if w in cache:
            stem = cache[w]
        else:
            stem = st.stem(w)
            cache[w] = stem
        return stem
else:
    def get_stem(w):
        return st.stem(w)

# 2. Get a category (a tuple) for a given word
def get_category(w):
    # Lookup in stem sets
    category_tuple = lookup_stem_sets(w)
    if category_tuple:
        return category_tuple

    if SPELLCHECKER_ENABLED:
        # Probably a typo, try suggestion from dictionary
        suggestion_stem = naive_checker.suggest(w)
        if suggestion_stem and suggestion_stem in c_stems:
            return c_stems[suggestion_stem]

    # Non-relevant word
    return None

def flat(d, out=[]):
    for val in d.values():
        if isinstance(val, dict):
            flat(val, out)
        else:
            out += val
    return out

## SPELLCHECKING ##

class NaiveSpellChecker:

    def __init__(self, wordlist):
        self.wordlist = []
        for w in wordlist:
            self.wordlist.append(get_stem(w))

        ### Build max distance vector
        # Words with length 4 < x <= 6 are only allowed to have one 'error', 
        # words with length 6 < x <= 8 -- no more than two 'errors', etc.
        input_v = [(5,0), (8,1), (10, 2)]
        self.max_dist_v = []
        prev = 0
        for t in input_v:
            max_len, max_dist = t
            self.max_dist_v += [max_dist] * (max_len - prev)
            prev = max_len
        # Expected output: [0, 0, 0, 0, 1, 1, 2, 2, 3, 3] 


    def get_max_distance(self, w):
        l = len(w)
        max_dist_v_len = len(self.max_dist_v) 
        if l > max_dist_v_len:
            l = max_dist_v_len
        return self.max_dist_v[l-1]

    def suggest(self, w):                  
        """Suggest a STEM"""
        if len(w) <= 2: return None
        # Use heap to store suggestions
        h = []
        max_distance = self.get_max_distance(w)
        w_stem = get_stem(w)
        for word in self.wordlist:
            dist = L.distance(word, w_stem)
            if dist > max_distance:
                continue
            el = (dist, word)
            heapq.heappush(h, el)
        if not h: return None
        distance, suggestion = heapq.heappop(h)
        return suggestion

if SPELLCHECKER_ENABLED:
    import Levenshtein as L 
    import heapq
    wordlist = flat(predictors_dict)
    naive_checker = NaiveSpellChecker(wordlist)

## MAIN ##

if __name__ == '__main__':
    init_reverse_index()
    for x in xrange(10000):
        get_category('incrases')
        get_category('increses')
    print get_category('increses')
    print get_category('increase')

