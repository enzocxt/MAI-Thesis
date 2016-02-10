#!/usr/bin/python

import os
import platform
import subprocess
import utils

# gSpan command:
# ./gspan -file [file_name] -support [support: float] &> log
# eclat command:
# ./eclat [options] infile [outfile]

class Mining(object):
    """Abstract class"""

    #def __init__(self, datafile=None, output=None):
    def __init__(self, inputs):
        # inputs{'type': 'itemset', 'matching': 'exact', 'constraints': 'frequency', 'dominance': 'max'}
        #self.inputs = inputs
        self.type = inputs['type']
        if inputs.has_key('matching'): self.matching = inputs['matching']
        else: self.matching = None
        if inputs.has_key('constraints'): self.constraints = inputs['constraints']
        else: self.constraints = None
        if inputs.has_key('dominance'): self.dominance = inputs['dominance']
        else: self.dominance = None
        if inputs.has_key('datafile'):
            self.datafile = os.getcwd() + '/' + inputs['datafile']
        else:
            print 'Need input data file!'
            sys.exit(2)
        if inputs.has_key('output'):
            self.output = os.getcwd() + '/' + inputs['output']
        else:
            print 'Need specify output file!'
            sys.exit(2)
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

    #def __init__(self, datafile, output, nsupport=None):
    def __init__(self, inputs):
        Mining.__init__(self, inputs)
        self.support = inputs['support']

    def mining(self):
        if platform.system() == "Linux":
          eclat = "./exec/eclat"
        else:
          eclat = "./exec/eclat"
        options = ""
        if self.dominance == 'max':
            options += '-tm'
        elif self.dominance == 'closed':
            options += '-tc'
        child = subprocess.Popen([eclat, options, self.datafile, self.output], stdout=subprocess.PIPE)
	print eclat, options, self.datafile, self.output
        fout = open(self.output, 'w')
        fout.write(child.stdout.read())
        fout.close()

    def parser(self):
        self.patternSet = utils.parser(self)
        return self.patternSet
