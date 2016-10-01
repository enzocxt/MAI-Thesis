"""
    author: Tao Chen
"""

import getopt
import ConfigParser
import collections
from collections import defaultdict
from tqdm import tqdm
from solver.method import *
from solver.generator import *
from solver.groupIDP import *
from solver.utils import logger
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support

default_parameters = 'config.ini'


# Debug print
def DebugPrint(s):
    print s


@logger
def fpMining_pure(inputs):
    if inputs['type'] == 'graph':
        inputs['data'] = 'data/gSpan/' + inputs['data']
        inputs['output'] = 'output/gSpan/' + inputs['output']
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        inputs['data'] = 'data/prefixSpan/' + inputs['data']
        inputs['output'] = 'output/prefixSpan/' + inputs['output']
        method = prefixSpan(inputs)
    elif inputs['type'] == 'itemset':
        inputs['data'] = 'data/eclat/' + inputs['data']
        inputs['output'] = 'output/eclat/' + inputs['output']
        method = eclat(inputs)
    else:
        print 'Does not support "type == %s"!' % inputs['type']
        sys.exit(2)

    output = method.mining()
    patterns = method.parser(output)
    print "\n*************************************"
    print 'Number of frequent patterns with constraints (pure exec): %s' % len(patterns)
    return patterns


@logger
def fpMining_IDP(inputs):
    if inputs['type'] == 'graph':
        if 'data/' not in inputs['data']:
            inputs['data'] = 'data/gSpan/' + inputs['data']
            inputs['output'] = 'output/gSpan/' + inputs['output']
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        if 'data/' not in inputs['data']:
            inputs['data'] = 'data/prefixSpan/' + inputs['data']
            inputs['output'] = 'output/prefixSpan/' + inputs['output']
        method = prefixSpan(inputs)
    elif inputs['type'] == 'itemset':
        if 'data/' not in inputs['data']:
            inputs['data'] = 'data/eclat/' + inputs['data']
            inputs['output'] = 'output/eclat/' + inputs['output']
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
    patterns = method.parser(output)    # frequent patterns, not closed
    '''
    print "\nNumber of frequent patterns: {0}\n".format(len(patterns))
    for p in patterns:
        print p
    '''

    if params['type'] == 'itemset':
        #indices = itemset_idp(params, patterns)
        #indices = itemset_idp_iterative(params, patterns)
        indices = itemset_idp_new(params, patterns)
    elif params['type'] == 'sequence':
        indices = sequence_idp_multiple(params, patterns)
    elif params['type'] == 'graph':
        #indices = graph_idp(params)
        pass
    '''
    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])
    # generate idp code for finding pattern with constraints
    idp_gen.gen_IDP_code(patterns, idp_program_name)
    # run generated idp code
    idp_output = idp_gen.run_IDP(idp_program_name)
    # parser the idp output
    indices = set(idp_gen.parser_from_stdout(idp_output))
    '''

    closed_patterns = []
    for p in patterns:
        if p.id in indices:
            closed_patterns.append(p)
    print "\n*************************************"
    print "\nNumber of {0} frequent patterns: {1}\n".format(params['dominance'], len(closed_patterns))

    return closed_patterns


def itemset_idp(params, patterns):
    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])
    # generate idp code for finding pattern with constraints
    idp_gen.gen_IDP_code(patterns, idp_program_name)
    # run generated idp code
    idp_output = idp_gen.run_IDP(idp_program_name)
    # parser the idp output
    indices = set(idp_gen.parser_from_stdout(idp_output))

    return indices


'''
def is_closed(pattern, mapping, support_mapping, idp_gen, idp_program_name_base):
    patterns_to_check = get_attribute_intersection(pattern, mapping, support_mapping)
    idp_program_name = '{0}_{1}'.format(idp_program_name_base, pattern.id)
    if patterns_to_check:
        idp_gen.gen_IDP_code(patterns_to_check, idp_program_name, pattern.id)
        idp_output = idp_gen.run_IDP(idp_program_name)
        if 'Unsatisfiable' in idp_output:
            return True
        else:
            return False
'''


def itemset_idp_new(params, patterns):
    indices = []

    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])

    if params['dominance'] == "closed":
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    mapping = make_attribute_mapping(patterns)

    return indices


def sequence_idp_multiple(params, patterns):
    indices = set([seq.id for seq in patterns])
    nonclosed_indices = set()

    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])

    if params['dominance'] == "closed":
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    attribute_mapping = make_attribute_mapping(patterns)

    ''' group testing '''
    mapping_groups = []
    for group in support_mapping.values():
        if len(group) == 1:
            print group
            continue
        check_mapping = defaultdict(set)
        for seq in group:
            patterns_to_check = get_attribute_intersection(seq, attribute_mapping, support_mapping)
            if len(patterns_to_check) > 1:
                check_mapping[seq] = patterns_to_check
        if check_mapping:
            mapping_groups.append(check_mapping)
    nonclosed_indices = async_mapping(mapping_groups, idp_gen, idp_program_name)
    #nonclosed_indices = async_mapping_withoutLock(mapping_groups, idp_gen, idp_program_name)

    '''
    lines = idp_output.split('\n')
    for line in lines:
        if 'selected_seq' in line:
            nonclosed_indices.add(int(line[19]))
    '''
    indices = indices - nonclosed_indices
    print indices

    return indices


def sequence_idp(params, patterns):
    for p in patterns:
        print p
    indices = set([seq.id for seq in patterns])
    nonclosed_indices = set()

    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])

    if params['dominance'] == "closed":
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    attribute_mapping = make_attribute_mapping(patterns)

    for support, group in support_mapping.items():
        if len(group) == 1:
            print group
            continue
        check_mapping = defaultdict(set)
        for seq in group:
            patterns_to_check = get_attribute_intersection(seq, attribute_mapping, support_mapping)
            if patterns_to_check:
                check_mapping[seq] = patterns_to_check

        if len(check_mapping.values()) != 0:
            idp_gen.gen_IDP_code_group(check_mapping, idp_program_name)
            idp_output = idp_gen.run_IDP(idp_program_name)

        lines = idp_output.split('\n')
        for line in lines:
            if 'selected_seq' in line:
                nonclosed_indices.add(int(line[19]))
    indices = indices - nonclosed_indices
    print indices

    '''
    for seq in tqdm(patterns):
        #if we make it a function, is_closed(seq)
        #then we need just need async_map(is_closed,patterns)
        patterns_to_check = get_attribute_intersection(seq,mapping,support_mapping)
        if len(patterns_to_check) > 1: #the pattern itself and other patterns
          # generate idp code for finding pattern with constraints for this seq
          idp_gen.gen_IDP_code(patterns_to_check, idp_program_name, seq.id)
          idp_output = idp_gen.run_IDP(idp_program_name)
          if 'Unsatisfiable' in idp_output:
              print(seq.id)
              os.system("cp IDP/closed_sequence_test.idp tmp/seq_test_{id}".format(id=seq.id))
              return # break here look at the INDEX, it should be 1 but it is 2 for some reason;
                     # the same for the case of id = 5, it is selected as 2 for some reason
              indices.append(seq.id)
        else:
          indices.append(seq.id)
    '''

    return indices


if __name__ == "__main__":
    # deal with command parameters
    if len(sys.argv) < 2:
        print 'Needs input file\n<wrapper.py -h> for help!'
        sys.exit(2)

    config_file = default_parameters        # config file path
    params = {}     # Dict to store input parameters

    try:
        # opts, args = getopt.getopt(sys.argv[1:], 'hc:i:o:', ['help=', 'config=', 'infile=', 'outfile='])
        opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['help=', 'config='])
    except getopt.GetoptError:
        print('wrapper.py -c <configfile>\nSet input data and output file in config file')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'wrapper.py -c <configfile> -i <inputfile> -o <outputfile>'
            sys.exit(2)
        #elif opt in ('-i', '--infile'):
        #    params['datafile'] = arg
        #elif opt in ('-o', '--outfile'):
        #    params['output'] = arg
        elif opt in ('-c', '--config'):
            config_file = arg

    # read parameters from config file
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
    #patterns = fpMining_pure(params)
    closed_patterns = fpMining_IDP(params)


    '''
    print "\n*************************************"
    print "Number of frequent patterns: {0}".format(len(patterns))

    freq = set([p for p in patterns])
    closed = set([p for p in closed_patterns])
    not_closed = freq- closed
    with open('tmp/test_output', "w") as test_out:
      test_out.write("------not_closed------"+"\n")
      for p in not_closed:
    # for p in patterns:
        test_out.write("id: "+str(p.id)+"\n")
        test_out.write("attributes: "+";".join(p.get_attributes())+"\n")
        test_out.write("support: " + str(p.get_support())+"\n")
      test_out.write("------frequent------"+"\n")
      for p in patterns:
        test_out.write("id: "+str(p.id)+"\n")
        test_out.write("attributes: "+";".join(p.get_attributes())+"\n")
        test_out.write("support: " + str(p.get_support())+"\n")
      test_out.write("------closed------"+"\n")
      for p in closed:
        test_out.write("id: "+str(p.id)+"\n")
        test_out.write("attributes: "+";".join(p.get_attributes())+"\n")
        test_out.write("support: " + str(p.get_support())+"\n")
      
    # test_out.write("------closed------"+"\n")
    # for p in closed_patterns:
    #   test_out.write("id: "+str(p.id)+"\n")
    #   test_out.write("attributes: "+";".join(p.get_attributes())+"\n")
    #   test_out.write("support: " + str(p.get_support())+"\n")
    '''

    '''
    print "Number of {0} frequent patterns: {1}".format(params['dominance'], len(closed_patterns))
    '''
