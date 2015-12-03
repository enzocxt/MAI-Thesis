#!/usr/bin/python

import subprocess
import sys, getopt
import utils
from fq_pattern import *

# gspan command:
# ./gspan -file [file_name] -support [support: float] &> log
# eclat command:
# ./eclat [options] infile [outfile]

class Mining(object):
    """Abstract class"""

    def __init__(self, datafile, output):
        self.datafile = datafile
        self.output = output
        self.patternSet = None

    def mining(self):
        abstract

class gSpan(Mining):
    """Use gSpan to mining frequent subgraphs"""

    def __init__(self, datafile, output, support):
        Mining.__init__(self, datafile, output)
        self.support = support
        #self.patternSet = None

    def mining(self):
        child = subprocess.Popen(['./gspan', '-file', self.datafile, '-support', self.support, '&>', self.output], stdout=subprocess.PIPE)
        fout = open(self.output, 'w')
        fout.write(child.stdout.read())
        fout.close()

    def parser(self):
        self.patternSet = utils.parser(self.output)

class eclat(Mining):
    """Use eclat to mining frequent itemsets"""

    def __init__(self, datafile, output, nsupport):
        Mining.__init__(self, datafile, output)
        self.support = nsupport

    def mining(self):
        pass

    def parser(self):
        pass

if __name__ == "__main__":
    method = sys.argv[1]
    datafile = ''
    output = ''
    support = 0

    try:
        opts, args = getopt.getopt(sys.argv[2:], 'i:s:o:', ['infile=', 'support=', 'outfile='])
    except getopt.GetoptError:
        print 'wrapper.py gSpan -i [infile_name] -s [support:float] -o [outfile_name]'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-i', '--infile'):
            datafile = arg
        elif opt in ('-o', '--outfile'):
            output = arg
        elif opt in ('-s', '--support'):
            support = arg
    
    gspan = gSpan(datafile, output, support)
    gspan.mining()
    gspan.parser()
    print len(gspan.patternSet)

    #child = subprocess.Popen([gspan_path, "-file", datafile, "-support", support, ">", outfile], stdout=subprocess.PIPE)
    #child.wait()
