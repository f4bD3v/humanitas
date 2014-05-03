#!/usr/bin/env python2

import sys
import os
import random
import enchant
from enchant.checker import SpellChecker

# Install nltk: 'sudo pip install -U pyyaml nltk'
from nltk.stem.lancaster import LancasterStemmer 
from nltk.metrics.distance import edit_distance

# Import predictor words (predictors_dict)
sys.path.append('../../../../analysis/twitter/keywords')
import predictors

# predictors_dict = 
#       { 'predict': { 'dec': ['decline'], 'inc': ['increase'] },
#         'price': { 'high': ['high'], 'low': ['low'] },
#         ... }
predictors_dict = predictors.predictors_dict

SPELLCHECKER_ENABLED = False

negative_forms = set(['not', 'no', 'non', 'nothing',
                  "don't", "dont", "doesn't", "doesnt",     # Present
                  "aren't", "arent", "a'int", "aint",
                  "isn't", "isnt",
                  "didn't", "didnt", "haven't", "havent",   # Past
                  "hasn't", "hasnt", "hadn't", "hadnt",
                  "weren't", "werent", "wasn't", "wasnt",
                  "wouldn't", "wouldnt",
                  "won't", "wont", "shan't", "shant",       # Future
                 ])

c_stems = {}
st = LancasterStemmer()

# 1. Build set for existing categories
def init_stem_sets():
    for dict_name in predictors_dict:
        category_dict = predictors_dict[dict_name]
        c_stems[dict_name] = {}
        for cname in category_dict:
            word_list = category_dict[cname]
            stem_set = set()
            for word in word_list:
                stem_set.add(st.stem(word))
            c_stems[dict_name][cname] = stem_set

def lookup_stem_sets(w):
    w = st.stem(w)
    for dict_name in c_stems:
        category_dict = c_stems[dict_name]
        for cname in category_dict:
            stem_set = category_dict[cname]
            if w in stem_set:
                return (dict_name, cname)
    return None

# 2. Get a category for a given word
def get_category(w):
    # Check if negation
    if w in negative_forms: return ('negation', None)
    # Lookup in stem sets
    category_tuple = lookup_stem_sets(w)
    if category_tuple: return category_tuple

    if SPELLCHECKER_ENABLED:
        # Probably a typo, try suggestion from dictionary
        suggestion = spellcheck(w)
        if suggestion:
            return lookup_stem_sets(suggestion)

    # Non-relevant word
    return None

## SPELLCHECKING ##

spellcheck_dict = enchant.PyPWL()
chkr = SpellChecker("en_US") 

def flatten(l):
    return reduce(lambda x, y: x+y, l)

def load_dict():
    for dict_name in predictors_dict:   
        category_dict = predictors_dict[dict_name]
        words = flatten(category_dict.values())
        for w in words:
            spellcheck_dict.add(w)

def spellcheck(w):
    min_word_length = 4
    edit_threshold = 3
    if chkr.check(w) or len(w) < min_word_length:
        # Word is correct or too short
        return None
    suggestions = spellcheck_dict.suggest(w)
    print suggestions
    if not suggestions:
        return None
    suggestion = suggestions[0]
    if edit_distance(w, suggestion) > edit_threshold:
        return None
    return suggestion

## MAIN ##

init_stem_sets()
load_dict()

print get_category('increases')

