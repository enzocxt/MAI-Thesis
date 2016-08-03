"""
    author: Tao Chen
"""

import getopt
import ConfigParser
from solver.method import *
from solver.generator import *

default_parameters = 'config.ini'


# Debug print
def DebugPrint(s):
    print s


# Method for mining frequent patterns
def fpMining(inputs):
    if inputs['type'] == 'graph':
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        method = prefixSpan(inputs)
    elif inputs['type'] == 'itemset':
        if 'dominance' in inputs:
            eclat_inputs = dict()
            for key in inputs:
                eclat_inputs[key] = inputs[key]
            eclat_inputs['dominance'] = ''
        method = eclat(eclat_inputs)
    else:
        print 'Does not support "type == %s"!' % inputs['type']
        sys.exit(2)

    output = method.mining()
    #print('\n\nOutput of eclat:\n%s' % output)
    patterns = method.parser(output)
    return patterns


def test(inputs):
    method = Mining(inputs)
    if inputs['type'] == 'graph':
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        method = prefixSpan(inputs)
    elif inputs['type'] == 'itemset':
        method = eclat(inputs)
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
    # deal with command parameters
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
    print('Parameters: %s' % params)

    # frequent pattern mining
    patterns = fpMining(params)
    print "\n*************************************"
    if patterns:
        print "Number of closed patterns: %s" % len(patterns)
        #for p in patterns:
        #    print p
    print "*************************************\n"

    # generate IDP code
    idp_gen = IDPGenerator(params)
    idp_program_name = '{0}_itemset_zoo'.format(params['dominance'])
    idp_gen.gen_IDP_code(patterns, idp_program_name)
    idp_output = idp_gen.run_IDP(idp_program_name)
    indices = set(idp_gen.parser_from_stdout(idp_output))
    print "\n*************************************"
    print "Number of closed frequent patterns: %s" % len(indices)
    for p in patterns:
        if p.id in indices:
            print p

    # Just for test
    '''
    print "\n*************************************"
    if patterns:
        print "Number of closed frequent patterns: %s" % len(patterns)
        #for i in range(10):
        #    print patterns[i]
    #print "Time cost by closed eclat is: %s" % t1
    #print "Number of closed frequent patterns (python): %s" % len(closedPatterns)
    #print "Time cost by python post-processing is: %s" % t2
    print "*************************************"
    '''