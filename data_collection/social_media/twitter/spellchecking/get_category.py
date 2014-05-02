#!/usr/bin/env python2

# Install nltk: 'sudo pip install -U pyyaml nltk'
from nltk.stem.lancaster import LancasterStemmer 

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

# 2. Get a category for a given word
def get_category(w):
    w_stem = st.stem(w)
    for cname in c: 
        stem_set = c_stems[cname]
        if w_stem in stem_set:
            return cname
    return None

init_stem_sets()
print c_stems
print get_category('increases')
