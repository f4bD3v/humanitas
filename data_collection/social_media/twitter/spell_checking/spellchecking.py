#!/usr/bin/env python2

import os
import random
import enchant
import time
import sys
import re
import Levenshtein as L
import heapq
from enchant.checker import SpellChecker as EnchantSpCheck
import aspell

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

class AspellChecker(SpChecker):

    def compile_dict(self, wordlist):
        infile = 'pr.dict.in'
        outfile = 'predictors.aspell.dict'
        
        with open(infile, 'wb') as f:
            for w in wordlist:
                # Aspell doesn't accept non-alpha characters like '-'
                w = re.sub(r'[^a-zA-Z]', '', w)
                f.write(w + "\n")
        
        # Compile dict
        cmd = 'aspell --lang=en create master ./%s < %s' % (outfile, infile)
        os.system(cmd)
        # Remove temp file
        os.remove(infile)
        self.dictfile = outfile

    def __init__(self, wordlist):
        SpChecker.__init__(self, wordlist)
        self.compile_dict(wordlist)
                
        params = [ ('master', './' + self.dictfile), 
                   ('master-path', './' + self.dictfile),]
        self.sp = aspell.Speller(*params)

        #config_keys = self.sp.ConfigKeys()

    def suggest(self, w):
        max_distance = 3
        w = re.sub(r'[^a-zA-Z]', '', w)
        suggestions = self.sp.suggest(w)
        if not suggestions:
            return None
        suggestion = suggestions[0]
        if L.distance(suggestion, w) > max_distance:
            return None
        else:
            return suggestion

def flat(d, out=[]):
    for val in d.values():
        if isinstance(val, dict):
            flat(val, out)
        else:
            out += val
    return out

def benchmark(checker):
    size = 10000
    total_time = 0.0
    print "### Measuring performance for ", checker
    for i in xrange(size):
        t1 = time.time()
        suggestion = checker.suggest('incrase')
        t2 = time.time()
        elapsed = t2 - t1
        total_time += elapsed
        if suggestion != 'increase':
            sys.exit('Bullshit!')
    avg_per_word = total_time / size
    print "Elapsed time:", total_time
    print "Average time per word:", avg_per_word
    print "Average speed:", 60 / avg_per_word, "(words/min)", \
                            3600 / avg_per_word, "(words/hour)"

if __name__ == "__main__":
    wordlist = flat(predictors_dict)

    # Very slow...
    enchant_sc = EnchantSpellChecker(wordlist)

    naive_sc = NaiveSpellChecker(wordlist)
    benchmark(naive_sc)

    print '= ' * 40

    aspell_sc = AspellChecker(wordlist)
    benchmark(aspell_sc)

