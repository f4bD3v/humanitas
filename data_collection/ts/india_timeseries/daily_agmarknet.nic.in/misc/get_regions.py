#!/usr/bin/env python2

import re
import os
import sys

# Extract region-state map from raw HTML files

region_dict = {}

def process_file(filename):
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    if len(lines) < 10:
        sys.exit('WTF? Invalid HTML')

    current_state = None
    for l in lines:
        match = re.search(r'<td colspan="8"><strong>(.+?)</strong>', l)
        if match:
            state_name = match.group(1)
            if state_name not in region_dict:
                region_dict[state_name] = []
            current_state = state_name
            continue

        match = re.match(r'<td width="[^"]+">([^<>]+?)</td>', l)
        if match:
            region_name = match.group(1).strip()
            if region_name == '': continue
            region_list = region_dict[current_state]
            if region_name not in region_list:
                region_list.append(region_name)
            


for root, dirs, files in os.walk('./raw_html'):
    for f in files:
        process_file(root + '/' + f)

check_dict = {}
outfile = open('regions.csv', 'w')
outfile.write("region,state\n\n")
for state in region_dict:
    for region in region_dict[state]:
        if region in check_dict:
            # TODO Region with the same name is already present, ignoring for now
            # print "### Adding '%s' to '%s': it already belongs to '%s'" % (region, state, check_dict[region]), 
            continue
        check_dict[region] = state
        region.replace(',', '_')
        state.replace(',', '_')
        outfile.write("%s,%s\n" % (region, state))
outfile.close()

