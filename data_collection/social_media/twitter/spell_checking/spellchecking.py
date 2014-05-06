#!/usr/bin/env python2

# Basic test for using 'enchant' spellchecking library

import os
import random
import enchant
import sys
import Levenshtein as L
import heapq
from enchant.checker import SpellChecker as EnchantSpCheck

sys.path.append('../../../../analysis/twitter/keywords/')
from predictors import predictors_dict as predictors_dict

class SpChecker:
    def __init__(self, wordlist):
        self.wordlist = wordlist

    def suggest(self, w):
        return None

class EnchantSpellChecker(SpChecker):

    def __init__(self, wordlist):
        SpChecker.__init__(self, wordlist)
        self.spdict = enchant.PyPWL()
        self.chkr = EnchantSpCheck("en_US")
        for w in self.wordlist:
            self.spdict.add(w)
    
    def suggest(self, w):
        min_word_length = 4 
        edit_threshold = 3 
        if self.chkr.check(w) or len(w) < min_word_length:
            # Word is correct or too short
            return None
        suggestions = self.spdict.suggest(w)
        if not suggestions:
            return None
        suggestion = suggestions[0]
        if L.distance(w, suggestion) > edit_threshold:
            return None
        return suggestion

class NaiveSpellChecker(SpChecker):

    def __init__(self, wordlist):
        SpChecker.__init__(self, wordlist)

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
        dist, suggestion = heapq.heappop(h)
        return suggestion

def flat(d, out=[]):
    for val in d.values():
        if isinstance(val, dict):
            flat(val, out)
        else:
            out += val
    return out

if __name__ == "__main__":
    wordlist = flat(predictors_dict)

    enchant_sc = EnchantSpellChecker(wordlist)
    naive_sc = NaiveSpellChecker(wordlist)
    for x in xrange(10000):
        res = naive_sc.suggest('incrase')
        #res = enchant_sc.suggest('incrase')
    print "# Output:\n", res
