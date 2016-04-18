import subprocess
import sys, getopt
import ConfigParser
import solver.utils
from solver.fqPattern import *
from solver.method import *

default_parameters = 'config.ini'

# Method for mining frequent patterns
def fpMining(inputs):
    method = Mining(inputs)
    if inputs['type'] == 'graph':
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        method = sequence(inputs)     # TO DO
    elif inputs['type'] == 'itemset':
        method = eclat(inputs)    # Use default support
    else:
        print 'Does not support "type == %s"!' % inputs['type']
        sys.exit(2)

    #t1 = method.mining()
    result = method.mining()
    patterns = method.parser(result)
    return patterns
    #closedPatterns, t2 = method.closedMining()
    #return patterns, t1, closedPatterns, t2


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print 'Needs input file\n<wrapper.py -h> for help!'
        sys.exit(2)

    config_file = default_parameters        # config file path
    params = {}     # Dict to store input parameters

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:i:o:', ['help=', 'config=', 'infile=', 'outfile='])
    except getopt.GetoptError:
        print('wrapper.py -c <configfile> -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'wrapper.py -c <configfile> -i <inputfile> -o <outputfile>'
            sys.exit(2)
        elif opt in ('-i', '--infile'):
            params['datafile'] = arg
        elif opt in ('-o', '--outfile'):
            params['output'] = arg
        elif opt in ('-c', '--config'):
            config_file = arg

    config = ConfigParser.ConfigParser()
    config.read(config_file)
    sections = config.sections()
    section = 'Parameters'
    options = config.options(section)
    for option in options:
        try:
            params[option] = config.get(section, option)
            if params[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            params[option] = None
    print params


    #patterns, t1, closedPatterns, t2 = fpMining(params)
    patterns = fpMining(params)

    # Just for test
    #fout = open('./output/time_cost.dat', 'a')
    #s = 10
    #while s <= 50:
    #    inputs['support'] = s
    #    patterns, t1, closedPatterns, t2 = fpMining(inputs)
    #    fout.write('%s\t%s\t%s\n' % (s, t1*1000, t2*1000))
    #    s += 2
    #fout.close()
    print "\n*************************************"
    print "Number of closed frequent patterns: %s" % len(patterns)
    #print "Time cost by closed eclat is: %s" % t1
    #print "Number of closed frequent patterns (python): %s" % len(closedPatterns)
    #print "Time cost by python post-processing is: %s" % t2
    print "*************************************"
