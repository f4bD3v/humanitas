#!/bin/bash

# Check if 'xls2csv' is installed
type xls2csv >/dev/null 2>&1 || \
    { echo >&2 "Install 'xls2csv', good sir, and then we'll continue our discussion."; exit 1; }

# Remove lots of repeated commas, leave only two from each group
xls2csv $1 | perl -pe 's/,,+/,,/g' 
