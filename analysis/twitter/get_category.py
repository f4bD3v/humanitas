#!/usr/bin/env python2

import sys

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
categories = []

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
            categories.append(str(dict_name)+'_'+str(cname))
            word_list = category_dict[cname]
            for word in word_list:
                stem = st.stem(word)
                c_stems[stem] = (dict_name, cname)
    # Add negative forms
    for word in negative_forms:
        c_stems[word] = ('negation', None)

def lookup_stem_sets(w):
    stem = st.stem(w)
    if stem in c_stems:
        return c_stems[stem]
    else:
        return None

# 2. Get a category (a tuple) for a given word
def get_category(w):
    # Lookup in stem sets
    category_tuple = lookup_stem_sets(w)
    if category_tuple:
        return category_tuple

    if SPELLCHECKER_ENABLED:
        # Probably a typo, try suggestion from dictionary
        suggestion = naive_checker.suggest(w)
        if suggestion:
            return lookup_stem_sets(suggestion)

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
        self.wordlist = wordlist

    def suggest(self, w):                  
        h = []
        max_distance = 3
        for word in self.wordlist:
            dist = L.distance(word, w)
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

