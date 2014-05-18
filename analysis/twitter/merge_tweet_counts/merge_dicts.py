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

def dump_csv():
    f = open('tweets_cities_regions_daily.csv', 'wb')
    for loc in out_dict: 
        loc_dict = out_dict[loc]
        for reg in loc_dict:
            reg_dict = loc_dict[reg]
            for day in reg_dict:
                cnt = reg_dict[day]
                s = "%s,%s,%s,%s" % (day, loc, reg, cnt)
                f.write(s + "\n")
    f.close()

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
    dump_csv()

if __name__ == '__main__':
    main()

