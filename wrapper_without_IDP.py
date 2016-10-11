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
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support, get_other_smaller_or_eq_patterns, group_by_len, create_smaller_or_eq_by_len_mapping, get_the_same_cover_sequences, get_the_same_cover_graphs
from solver.subsumption import SumsumptionLattice
from solver.Constraint import LengthConstraint, IfThenConstraint, CostConstraint


default_parameters = 'config.ini'

def process_constraints_sequences(params,patterns):
    constraints = params['constraints']

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

    if params['type'] == 'itemset':
        # indices = itemset_idp(params, patterns)
        pass
    elif params['type'] == 'sequence':
        patterns_pruned = list(process_constraints_sequences(params, patterns))
        indices = sequence_mining(params, patterns_pruned)
    elif params['type'] == 'graph':
        patterns_pruned = list(process_constraints_sequences(params, patterns))
        indices = graph_mining(params, patterns_pruned)

    closed_patterns = []
    for p in patterns:
        if p.id in indices:
            closed_patterns.append(p)
    print "\n*************************************"
    print "\nNumber of {0} frequent patterns: {1}\n".format(params['dominance'], len(closed_patterns))

    return closed_patterns


def sequence_mining(params, patterns):
    indices = []

    if params['dominance'] == "closed" or params['dominance'] == "free" :
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    subsumLattice = SumsumptionLattice(patterns)
    lattice = subsumLattice.get_lattice()
    skip_set = set([])

    for seq in tqdm(sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)):
        if seq in skip_set:
          # print('skipping the sequence', seq)
            continue

        prune_patterns = set(subsumLattice.get_all_children(seq, lattice))
        children = set(subsumLattice.get_all_children(seq,lattice))

        if params['dominance'] == "closed":
            the_same_sup   = set(support_mapping[seq.get_support()])
            prune_patterns = get_the_same_cover_sequences(seq,children.intersection(the_same_sup))
            indices.append(seq.id)
        elif params['dominance'] == "maximal":  # simply speaking in case of maximal -- prune the whole subtree
            prune_patterns = children 
            indices.append(seq.id)
        elif params['dominance'] == "free":
            the_same_sup   = set(support_mapping[seq.get_support()])
            prune_patterns = get_the_same_cover_sequences(seq,children.intersection(the_same_sup))
            prune_patterns.add(seq)
            leaves         = subsumLattice.get_leaves(prune_patterns, lattice)
            for leaf in leaves:
                indices.append(leaf.id)


        skip_set |= prune_patterns

    return indices


def graph_mining(params, patterns):
    print('\nNumber of patterns: %s' % len(patterns))
    indices = []

    if params['dominance'] == "closed" or params['dominance'] == "free" :
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    subsumLattice = SumsumptionLattice(patterns)
    lattice = subsumLattice.get_lattice()
    #for i in lattice.values():
    #    print len(i)

    skip_set = set([])

    for graph in tqdm(sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)):
        if graph in skip_set:
          # print('skipping the sequence', seq)
            continue

        prune_patterns = set(subsumLattice.get_all_children(graph, lattice))
        children = set(subsumLattice.get_all_children(graph, lattice))

        if params['dominance'] == "closed":
            the_same_sup   = set(support_mapping[graph.get_support()])
            prune_patterns = get_the_same_cover_graphs(graph, children.intersection(the_same_sup))
            indices.append(graph.id)
        elif params['dominance'] == "maximal":  # simply speaking in case of maximal -- prune the whole subtree
            prune_patterns = children
            indices.append(graph.id)
        elif params['dominance'] == "free":
            the_same_sup   = set(support_mapping[graph.get_support()])
            prune_patterns = get_the_same_cover_sequences(graph, children.intersection(the_same_sup))
            prune_patterns.add(graph)
            leaves         = subsumLattice.get_leaves(prune_patterns, lattice)
            for leaf in leaves:
                indices.append(leaf.id)

        skip_set |= prune_patterns

    return indices


if __name__ == "__main__":
    # deal with command parameters
    if len(sys.argv) < 2:
        print 'Needs input file\n<wrapper.py -h> for help!'
        sys.exit(2)

    config_file = default_parameters        # config file path
    params = {}     # Dict to store input parameters

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hc:', ['help=', 'config='])
    except getopt.GetoptError:
        print('wrapper.py -c <configfile>\nSet input data and output file in config file')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'wrapper.py -c <configfile> -i <inputfile> -o <outputfile>'
            sys.exit(2)
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
   
    # read constraints
    section = 'Constraints'
    options = config.options(section)
    params['constraints'] = dict()
    for option in options:
        if option == 'length':
            max_len = int (config.get(section, option))
            params['constraints']['length'] = LengthConstraint(max_len)
        elif option == 'ifthen':
            pre, post = config.get(section, option).split(';')
            params['constraints']['ifthen'] = IfThenConstraint(int(pre), int(post))
        elif option == 'cost':
            cost_mapping = collections.defaultdict(int)
            costs = config.get(section, option).split(';')
            costs, max_cost = costs[:-1], costs[-1].split(':')[-1]
            for c in costs:
                id, cost = c.split(':')
                cost_mapping[int(id)] = int(cost)
            params['constraints']['cost'] = CostConstraint(int(max_cost), cost_mapping)
        else:
            print("Does not support this type of constraint: %s" % option)


    # frequent pattern mining
    #patterns = fpMining_pure(params)
    #for i in range(10):
    #    print patterns[i].get_graphx().nodes(data=False)
    closed_patterns = fpMining_IDP(params)


    print "\n*************************************"
    print "Number of frequent patterns: {0}".format(len(closed_patterns))

    '''
    print "Number of {0} frequent patterns: {1}".format(params['dominance'], len(closed_patterns))
     '''
