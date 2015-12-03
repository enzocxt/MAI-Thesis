#!/usr/bin/python

import subprocess
import sys, getopt
from fq_pattern import *
from utils import parser

# gspan command:
# ./gspan -file [file_name] -support [support: float] &> log
# python command:
# python pygSpan.py -i [file_name] -s [support: float] -o [outfile_name]

gspan_path = './gspan'
datafile = ''
outfile = ''
support = 0

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:s:o:', ['infile=', 'support=', 'outfile='])
except getopt.GetoptError:
    print 'pyeclat -i [file_name] -s [support:float] -o [file_name]'
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-i', '--infile'):
        datafile = arg
    elif opt in ('-o', '--outfile'):
        outfile = arg
    elif opt in ('-s', '--support'):
        support = arg

#child = subprocess.Popen([gspan_path, "-file", datafile, "-support", support, "&>", outfile])
command = "%s -file %s -support %s &> %s" % (gspan_path, datafile, support, outfile)
print command
#child = subprocess.Popen(["./gspan", "-file", "./Chemical_340", "-support", "0.1", "&>", "./log_12032015"])
child = subprocess.Popen("" + command)
#retcode = subprocess.call(command)
print "Child process starting"
