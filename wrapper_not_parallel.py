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
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support, get_other_smaller_or_eq_patterns, group_by_len,create_smaller_or_eq_by_len_mapping
from solver.subsumption import create_subsumption_lattice, get_all_children, get_direct_children, read_negative_dataset_sequences
from solver.Constraint import SequenceLengthConstraint, SequenceIfThenConstraint, SequenceCostConstraint


default_parameters = 'config.ini'

def process_constraints_sequences(params,patterns):
    constraints = params['constraints']
    print(constraints)
    for pattern in patterns:
      is_valid = True
      for constraint in constraints.values():
        if not constraint.is_valid(pattern):
          is_valid = False
          break
      if is_valid:
        yield pattern
        




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
        # first call constraints check method to generate idp program
        # and check the patterns with constraints
        patterns_pruned = list(process_constraints_sequences(params,patterns))
#       indices = set(sequence_idp_constraints(params, patterns))
#       patterns_pruned = []
#       for p in patterns:
#           if p.id in indices:
#               patterns_pruned.append(p)

        indices = sequence_idp(params, patterns_pruned)
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


def sequence_idp_constraints(params, patterns):
    indices = []
    constraints = params['constraints']

    idp_gen = IDPGenerator(params)
    path, filename = os.path.split(params['data'])
    idp_program_name = '{0}_{1}_{2}'.format('posprocessing', params['type'], filename.split('.')[0])
  # print("IDP NAME", idp_program_name)
    idp_gen.gen_IDP_sequence_constraints(constraints, patterns, idp_program_name)
    idp_output = idp_gen.run_IDP(idp_program_name)
    for line in idp_output.split('\n'):
        if 'output' in line:
            ids = line.split('=')[-1]
            ids = ids.replace(' ', '').replace('{','').replace('}','')
            indices = [int(id) for id in ids.split(';')]
            break
    return indices


def sequence_idp(params, patterns):
    

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
    smaller_or_eq_mapping = create_smaller_or_eq_by_len_mapping(mapping_by_len)

    #for debuggin only
    os.system("rm tmp/seq_test_*")
    number_of_IDP_calls = 0

    lattice = create_subsumption_lattice(patterns)
    not_solution_set = set([])

    for seq in tqdm(sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)):
        if seq in not_solution_set:
          # print('pruning the sequence', seq)
            continue
        indices.append(seq.id)

        prune_patterns = set(get_all_children(seq,lattice))
          
        if params['dominance'] == "closed":
            the_same_sup   = set(support_mapping[seq.get_support()])
            prune_patterns = prune_patterns.intersection(the_same_sup)
        # elif params['dominance'] == "maximal":  # simply speaking in case of maximal -- prune the whole subtree
        #     prune_patterns = prune_patterns
        not_solution_set |= prune_patterns

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

    # read basic parameters
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

    print(read_negative_dataset_sequences(params['negative']))

    # read constraints
    section = 'Constraints'
    options = config.options(section)
    params['constraints'] = dict()
    for option in options:
        if option == 'length':
            max_len = int (config.get(section, option))
            params['constraints']['length'] = SequenceLengthConstraint(max_len)
        elif option == 'ifthen':
            pre, post = config.get(section, option).split(';')
            params['constraints']['ifthen'] = SequenceIfThenConstraint(int(pre), int(post))
        elif option == 'cost':
            cost_mapping = collections.defaultdict(int)
            costs = config.get(section, option).split(';')
            costs, max_cost = costs[:-1], costs[-1].split(':')[-1]
            for c in costs:
                id, cost = c.split(':')
                cost_mapping[int(id)] = cost
            params['constraints']['cost'] = SequenceCostConstraint(int(max_cost), cost_mapping)
        else:
            print("Does not support this type of constraint: %s" % option)


    # frequent pattern mining
    patterns = fpMining_pure(params)
    closed_patterns = fpMining_IDP(params)


    print "\n*************************************"
    print "Number of frequent patterns: {0}".format(len(patterns))

    '''
    print "Number of {0} frequent patterns: {1}".format(params['dominance'], len(closed_patterns))
     '''
