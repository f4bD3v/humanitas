#!/bin/bash

# Check if 'xls2csv' is installed
type xls2csv >/dev/null 2>&1 || \
    { echo -n >&2 "
Install 'xls2csv', good sir, and then we'll continue our discussion.
(xls2csv is a part of 'catdoc' package which is released for all major OSes)

"; exit 1; }

# Remove lots of repeated commas, leave only two from each group
xls2csv $1 | perl -pe 's/,,+/,/g'
