"""
    author: Tao Chen
"""

import getopt
import ConfigParser
import collections
from tqdm import tqdm
from solver.method import *
from solver.generator import *
from solver.utils import logger
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support, get_other_smaller_or_eq_patterns, group_by_len
from solver.subsumption import create_subsumption_lattice

default_parameters = 'config.ini'


# Debug print
def DebugPrint(s):
    print s

with open("tmp/sergey_tmp_log","w"): # clean the log file before each run
    pass

def sergeylog(s): #dump info into the log file
    with open("tmp/sergey_tmp_log","a") as logfile:
        logfile.write(s)



# Method for mining frequent patterns
def fpMining(inputs):
    if inputs['type'] == 'graph':
        method = gSpan(inputs)
    elif inputs['type'] == 'sequence':
        method = prefixSpan(inputs)
    elif inputs['type'] == 'itemset':
        method = eclat(inputs)
    else:
        print 'Does not support "type == %s"!' % inputs['type']
        sys.exit(2)

    output = method.mining()
    patterns = method.parser(output)
    return patterns


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
        indices = itemset_idp_iterative(params, patterns)
    elif params['type'] == 'sequence':
        indices = sequence_idp(params, patterns)
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


def itemset_idp_iterative(params, patterns):
    indices = set()

    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])

    groups = collections.defaultdict(list)
    # group itemset with same support to different groups
    for p in patterns:
        groups[p.support].append(p)
    groups = list(groups.values())
    for i in tqdm(range(len(groups))):
        group = groups[i]
        print 'Number of itemsets with support {0}: {1}'.format(group[0].support, len(group))
        idp_gen.gen_IDP_code(group, idp_program_name)
        idp_output = idp_gen.run_IDP(idp_program_name)
        '''
        for itemset in group:
            # generate idp code for finding pattern with constraints
            idp_gen.gen_IDP_code(group, idp_program_name, itemset.id)
            idp_output = idp_gen.run_IDP(idp_program_name)
            if 'Unsatisfiable' in idp_output:
                indices.append(itemset.id)
        '''
        indices.union(set(idp_gen.parser_from_stdout(idp_output)))

    return indices


# this method is not used now
def itemset_idp_iterative_old(params, patterns):
    indices = []

    # closed pattern mining by generated IDP code
    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format(params['dominance'], params['type'], filename.split('.')[0])
    for i in tqdm(range(len(patterns))):
        itemset = patterns[i]
        # generate idp code for finding pattern with constraints
        idp_gen.gen_IDP_code(patterns, idp_program_name, itemset.id)
        idp_output = idp_gen.run_IDP(idp_program_name)
        if 'Unsatisfiable' in idp_output:
            indices.append(itemset.id)

    return indices


def sequence_idp(params, patterns):
    
    subsumption_tree = create_subsumption_lattice(patterns)


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
    mapping_by_len = group_by_len(patterns)

    #for debuggin only
    os.system("rm tmp/seq_test_*")
    number_of_IDP_calls = 0
    

    for seq in tqdm(patterns):
        #if we make it a function, is_closed(seq)
        #then we need just need async_map(is_closed,patterns)
        patterns_to_check = get_attribute_intersection(seq,mapping,support_mapping)
        patterns_to_check = patterns_to_check - get_other_smaller_or_eq_patterns(seq, mapping_by_len)
        if len(patterns_to_check) > 1: #the pattern itself and other patterns
          number_of_IDP_calls += 1
          # generate idp code for finding pattern with constraints for this seq
          idp_gen.gen_IDP_code(list(patterns_to_check), idp_program_name, seq.id)
          idp_output = idp_gen.run_IDP(idp_program_name)

          print("running idp on id=",seq.id)
          os.system("cp IDP/{program}.idp tmp/seq_test_{id}.idp".format(id=seq.id, program=idp_program_name))
          if 'Unsatisfiable' in idp_output:
#             return # break here look at the INDEX, it should be 1 but it is 2 for some reason;
                     # the same for the case of id = 5, it is selected as 2 for some reason
              indices.append(seq.id)
              sergeylog("run idp on {id}, it failed, solution\n".format(id=seq.id))
          else:
              sergeylog("run idp on {id}, it succeeded, not a solution\n".format(id=seq.id)) 
              sergeylog("IDP OUTPUT: \n")
              sergeylog(idp_output)
              sergeylog("\n")
        else:
          indices.append(seq.id)

    print("NUMBER OF IDP CALLS",number_of_IDP_calls)
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
    patterns = fpMining_pure(params)
    closed_patterns = fpMining_IDP(params)


    print "\n*************************************"
    print "Number of frequent patterns: {0}".format(len(patterns))

#   freq = set([p for p in patterns])
#   closed = set([p for p in closed_patterns])
#   not_closed = freq - closed
#   with open('tmp/test_output', "w") as test_out:
#     test_out.write("------not_closed------"+"\n")
#     for p in not_closed:
#       test_out.write("id: "+str(p.id)+"\n")
#       test_out.write("attributes: "+";".join(map(lambda x: str(x),p.get_attributes()))+"\n")
#       test_out.write("support: " + str(p.get_support())+"\n")
#     test_out.write("------frequent------"+"\n")
#     for p in patterns:
#       test_out.write("id: "+str(p.id)+"\n")
#       test_out.write("attributes: "+";".join(map(lambda x: str(x),p.get_attributes()))+"\n")
#       test_out.write("support: " + str(p.get_support())+"\n")
#     test_out.write("------closed------"+"\n")
#     for p in closed:
#       test_out.write("id: "+str(p.id)+"\n")
#       test_out.write("attributes: "+";".join(map(lambda x: str(x),p.get_attributes()))+"\n")
#       test_out.write("support: " + str(p.get_support())+"\n")
#     
    # test_out.write("------closed------"+"\n")
    # for p in closed_patterns:
    #   test_out.write("id: "+str(p.id)+"\n")
    #   test_out.write("attributes: "+";".join(p.get_attributes())+"\n")
    #   test_out.write("support: " + str(p.get_support())+"\n")

    '''
    print "Number of {0} frequent patterns: {1}".format(params['dominance'], len(closed_patterns))
    '''
