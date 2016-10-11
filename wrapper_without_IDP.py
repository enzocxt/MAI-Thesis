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
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support, get_other_smaller_or_eq_patterns, group_by_len, create_smaller_or_eq_by_len_mapping, get_the_same_cover_sequences
from solver.subsumption import SumsumptionLattice
from solver.Constraint import LengthConstraint, IfThenConstraint, CostConstraint


default_parameters = 'config.ini'

def process_constraints(params,patterns):
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
        inputs['output'] = 'output/gSpan' + inputs['output']
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
            inputs['output'] = 'output/gSpan_' + inputs['output']
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
    patterns = method.parser(output)    # frequent patterns, not closed, not constrainted

    if params['type'] == 'itemset':
        # indices = itemset_idp(params, patterns)
        pass
    else:
        print "# of patterns", len(patterns)
        patterns_pruned = list(process_constraints(params, patterns))
        print "# of constrained patterns", len(patterns_pruned)
        final_patterns  = list(dominance_check(params, patterns_pruned))
        print "# of dominance patterns", len(final_patterns)


    return final_patterns


def dominance_check(params, patterns):
    indices = []

    if params['dominance'] == "closed" or params['dominance'] == "free" :
      support_mapping = make_grouping_by_support(patterns)
    else:
      support_mapping = None

    subsumLattice = SumsumptionLattice(patterns)
    skip_set = set([])

    for pattern in tqdm(sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)):
        if pattern in skip_set:
          # print('skipping the sequence', seq)
            continue

        prune_patterns = set(subsumLattice.get_all_children(pattern))
        children = set(subsumLattice.get_all_children(pattern))

        if params['dominance'] == "closed":
            the_same_sup   = set(support_mapping[pattern.get_support()])
           #prune_patterns = get_the_same_cover_sequences(seq,children.intersection(the_same_sup)) # need to use only if the tree is based not on the sub-pattern relationalship
            prune_patterns = children.intersection(the_same_sup)
            indices.append(pattern.id)
        elif params['dominance'] == "maximal":  # simply speaking in case of maximal -- prune the whole subtree
            prune_patterns = children 
            indices.append(pattern.id)
        elif params['dominance'] == "free":
            the_same_sup   = set(support_mapping[pattern.get_support()])
           #prune_patterns = get_the_same_cover_sequences(seq,children.intersection(the_same_sup)) # need to use only if the tree is based not on the sub-pattern relationalship
            prune_patterns = children.intersection(the_same_sup)
            prune_patterns.add(pattern)
            leaves         = subsumLattice.get_leaves(prune_patterns)
            for leaf in leaves:
                indices.append(leaf.id)


        skip_set |= prune_patterns

    for p in patterns:
        if p.id in indices:
            yield p




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
  # print "Number of frequent patterns: {0}".format(len(patterns))
    print "Number of {0} patterns: {1}".format(params['dominance'], len(closed_patterns))
