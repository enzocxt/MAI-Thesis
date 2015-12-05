#!/usr/bin/python

import subprocess
import utils

# gSpan command:
# ./gspan -file [file_name] -support [support: float] &> log
# eclat command:
# ./eclat [options] infile [outfile]

class Mining(object):
    """Abstract class"""

    def __init__(self, datafile=None, output=None):
        self.datafile = datafile
        self.output = output
        self.patternSet = None

    def mining(self):
        pass

    def parser(self):
        pass

class gSpan(Mining):
    """Use gSpan to mining frequent subgraphs"""

    def __init__(self, datafile, output, support):
        Mining.__init__(self, datafile, output)
        self.support = support

    def mining(self):
        child = subprocess.Popen(['./gspan', '-file', self.datafile, '-support', self.support, '&>', self.output], stdout=subprocess.PIPE)
        fout = open(self.output, 'w')
        fout.write(child.stdout.read())
        fout.close()

    def parser(self):
        self.patternSet = utils.parser(self)

class eclat(Mining):
    """Use eclat to mining frequent itemsets"""

    def __init__(self, datafile, output, nsupport=None):
        Mining.__init__(self, datafile, output)
        self.support = nsupport

    def mining(self):
        child = subprocess.Popen(['./eclat', '-s', self.datafile, self.output], stdout=subprocess.PIPE)
        fout = open(self.output, 'w')
        fout.write(child.stdout.read())
        fout.close()

    def parser(self):
        self.patternSet = utils.parser(self)
        return self.patternSet
