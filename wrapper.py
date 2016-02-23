#!/usr/bin/python

import subprocess
import sys, getopt
import solver.utils
from solver.fqPattern import *
from solver.method import *


# Method for mining frequent patterns
def fpMining(inputs):
    method = Mining(inputs)
    if inputs['type'] == 'graph':
        method = gSpan(inputs)    # TO DO
    elif inputs['type'] == 'sequence':
        method = sequence(inputs)     # TO DO
    elif inputs['type'] == 'itemset':
        method = eclat(inputs)    # Use default support
    else:
        print 'Does not support "type == %s"!' % inputs['type']
        sys.exit(2)

    t1 = method.mining()
    patterns = method.parser()
    #method.closedMining()
    closedPatterns, t2 = method.closedMining()
    if not closedPatterns:
        closedPatterns = [1]
    return patterns, t1, closedPatterns, t2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Needs parameters!'
        sys.exit(2)
    method = sys.argv[1]
    inputs = {}     # Dict to store input parameters

    # Parse the parameters
    # Currently, could only dealt with --type, --infile, --outfile
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'T:M:C:D:i:s:o:', ['type=', 'matching', 'constraint=', 'dominance=', 'infile=', 'support=', 'outfile='])
    except getopt.GetoptError:
        print 'wrapper.py -T [graph] -M [exact] -C [frequency] -D [closed] \
              -i [infile_name] -s [support:float] -o [outfile_name]'
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-T', '--type'):
            inputs['type'] = arg
        elif opt in ('-M', '--matching'):
            inputs['matching'] = arg
        elif opt in ('-C', '--constraint'):
            inputs['constraint'] = arg
        elif opt in ('-D', '--dominance'):
            inputs['dominance'] = arg
        elif opt in ('-i', '--infile'):
            inputs['datafile'] = arg
        elif opt in ('-o', '--outfile'):
            inputs['output'] = arg
        elif opt in ('-s', '--support'):
            inputs['support'] = arg

    patterns, t1, closedPatterns, t2 = fpMining(inputs)
    print "\n*************************************"
    print "Number of frequent patterns: %s" % len(patterns)
    print "Time cost by closed eclat is: %s" % t1
    print "Number of closed frequent patterns: %s" % len(closedPatterns)
    print "Time cost by python post-processing is: %s" % t2
    print "*************************************"
