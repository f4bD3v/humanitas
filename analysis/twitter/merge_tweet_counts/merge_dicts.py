#!/usr/bin/env python

import os
import sys
import pickle
from glob import glob

out_dict = {'cities' : {}, 'regions' : {}}


def load_dict(filename):
    with open(filename, 'r') as f:
        d = pickle.load(f)
    print "### Loaded dictionary from", filename
    return d

def add_dict_location(d, cat, loc):
    if loc not in out_dict[cat]:
        out_dict[cat][loc] = {}
    out_dict_loc = out_dict[cat][loc]
    d_loc = d[cat][loc]
    for date in d_loc:
        if date not in out_dict_loc:
            out_dict_loc[date] = 0
        out_dict_loc[date] += d_loc[date]

def add_dict(d):
    for category in ['cities', 'regions']:
        d_cat = d[category]
        for loc in d_cat:
            add_dict_location(d, category, loc)

def main():
    files = glob('out*.pickle')
    dicts = []
    for f in files:
        dicts.append(load_dict(f))

    for d in dicts:
        add_dict(d)

    out_file = 'tweets_india_cnt.pickle'
    with open(out_file, 'wb') as f:
        pickle.dump(out_dict, f)
    print "# Saved output to", out_file

if __name__ == '__main__':
    main()

