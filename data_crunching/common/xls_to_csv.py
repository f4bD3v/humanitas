#!/usr/bin/env python2

import os
import sys
import re

def usage():
    print """
xls_to_csv.py converts a file or several files (all it can find under the specified directory) from .xls/.xlsx format to CSV, saving them with the same base names and '.csv' extension.

Usage:

    python2 xls_to_csv.py {FILE|DIR}

Examples:

    python2 xls_to_csv.py ./data/india/xls/India_rice_2.xls
    python2 xls_to_csv.py ./data
    """

# portable 'which'
# (from https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python)
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

def check_xls2csv():
    if not which('xls2csv'):

        print """
Install 'xls2csv', good sir, and then we'll continue our discussion.
(xls2csv is a part of 'catdoc' package which is released for all major OSes)
"""
        sys.exit(1)

def process_file(filepath):
    path_no_ext, ext = os.path.splitext(filepath)
    if not ext in ['.xls', '.xlsx']:
        return
    out_file = path_no_ext + '.csv'
    # CONVERT!
    print "Processing:", filepath
    exec_str = "xls2csv %s 2> /dev/null | perl -pe 's/,,+/,/g' > %s" % (filepath, out_file)
    os.system(exec_str)

def process_dir(dirpath):
    for root, dirs, files in os.walk(dirpath): # Walk directory tree
        for f in files:
            filepath = root + '/' + f
            process_file(filepath) 

def main(path):
    check_xls2csv()
    # Change current directory
    script_dir = os.path.dirname(sys.argv[0])
    os.chdir(script_dir)
    full_current_path = os.getcwd()
    # Get absolute path of the given path
    if not os.path.isabs(path):
        path = os.path.abspath(full_current_path + '/' + path)
     
    if os.path.isfile(path):
        if not os.path.splitext(path)[1] in ['.xls', '.xlsx']:
            print 'Is it a XLS/XLSX file?'
            sys.exit(1)
        process_file(path)
    elif os.path.isdir(path):
        process_dir(path)
    else:
        print 'File or directory does not exist.'
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1 or sys.argv[1] in ['-h', '--help']:
        usage()
        sys.exit(0)

    main(sys.argv[1])
