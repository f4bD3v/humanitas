#!/usr/bin/env python2

# Install nltk: 'sudo pip install -U pyyaml nltk'
from nltk.stem.lancaster import LancasterStemmer 

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


c = {'cname1': ['hello', 'rice', 'increasing'], 'cname2': ['horses', 'horse']}

c_stems = {}
st = LancasterStemmer()

# 1. Build set for existing categories
def init_stem_sets():
    for cname in c:
        word_list = c[cname]
        stem_set = set()
        for word in word_list:
            stem_set.add(st.stem(word))
        c_stems[cname] = stem_set


def lookup_stem_sets(w):
    w = st.stem(w)
    for cname in c: 
        stem_set = c_stems[cname]
        if w in stem_set:
            return cname
    return None

# 2. Get a category for a given word
def get_category(w):
    # Check if negation
    if w in negative_forms: return 'Negation'
    # Lookup in stem sets
    category = lookup_stem_sets(w)
    if category: return category
    # Probably, there's a typo, try suggestions
    return None

init_stem_sets()
print c_stems
print get_category('meow')
