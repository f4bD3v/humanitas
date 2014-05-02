#!/usr/bin/env python2

# Basic test for using 'enchant' spellchecking library

import os
import random
import enchant
from enchant.checker import SpellChecker

dict_base = '../azure/words/'
dict_files = ['food-words-india.txt', 'predictor-words-india.txt', 'region-words-india.txt', 'food-words-indo.txt', 'predictor-words-indo.txt', 'region-words-indo.txt']

pwls = []

def open_dicts():
    global pwls
    os.chdir(dict_base) 
    for d in dict_files:
        pwl = enchant.request_pwl_dict(d)
        pwls.append(pwl)

def suggest_from_dicts(w):
    for pwl in pwls:
        suggestion = pwl.suggest(w)
        if suggestion:
            return suggestion[0]
    return None

def spellcheck(s):
    open_dicts()
    chkr = SpellChecker("en_US")
    words = s.split()
    out_words = []
    for w in words:
        if len(w) <= 3 or chkr.check(w):
            out_word = w
        else:
            out_word = suggest_from_dicts(w)
            if not out_word:
                out_word = w
        out_words.append(out_word)

    res_str = ' '.join(out_words)
    return res_str

s = "I want som rcee and banna, in indiaa"
print "# Input:\n", s
res = spellcheck(s)
print "# Output:\n", res
