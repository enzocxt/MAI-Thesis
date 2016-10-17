"""
    author: Tao Chen
"""

import getopt
import ConfigParser
import collections
import time
from tqdm import tqdm
from solver.method import *
from solver.generator import *
from solver.utils import logger
from solver.data_structures import make_attribute_mapping, get_attribute_intersection, make_grouping_by_support, get_other_smaller_or_eq_patterns, group_by_len, create_smaller_or_eq_by_len_mapping, get_the_same_cover_itemsets, get_the_same_cover_sequences, get_the_same_cover_graphs
from solver.subsumption import SubsumptionLattice
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


@logger
def fpMining_pure(inputs):
    if inputs['type'] == 'graph':
        inputs['data'] = 'data/gSpan/' + inputs['data']
        inputs['output'] = 'output/gSpan/' + inputs['output']
        #inputs['output'] = 'output/gSpan_' + inputs['output']
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

    start1   = time.time()
    output   = method.mining()
    patterns = method.parser(output)
    end1     = time.time()
    print "\n*************************************"
    print 'Number of frequent patterns with constraints (pure exec): %s' % len(patterns)

    return patterns, end1-start1


@logger
def fpMining_postpro(inputs):
    if inputs['type'] == 'graph':
        if 'data/' not in inputs['data']:
            inputs['data'] = 'data/gSpan/' + inputs['data']
            inputs['output'] = 'output/gSpan/' + inputs['output']
            #inputs['output'] = 'output/gSpan_' + inputs['output']
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

    params = inputs
    # step 1 time cost
    start1   = time.time()
    output   = method.mining()
    patterns = method.parser(output)    # frequent patterns, not closed, not constrainted
    end1     = time.time()
    print "# of patterns", len(patterns)
    start2   = time.time()
    patterns_pruned = process_constraints(params, patterns)
    if patterns_pruned:
        patterns_pruned = list(patterns_pruned)
    else: patterns_pruned = []
    end2     = time.time()
    print "# of constrained patterns", len(patterns_pruned)
    start3   = time.time()
    final_patterns = dominance_check(params, patterns_pruned)
    if final_patterns:
        final_patterns = list(final_patterns)
    else: final_patterns = []
    print "# of dominance patterns", len(final_patterns)
    end3     = time.time()
 
    print("step1:", end1-start1, "step2:", end2-start2, "step3:", end3-start3)
    return final_patterns, end1-start1, end2-start2, end3-start3


def dominance_check(params, patterns):
    subsumLattice = SubsumptionLattice()
    output_patterns = subsumLattice.check_dominance(patterns,params)
    return output_patterns
#   skip_set = set([])

#   if params['type'] == "graph":
#     print('using pareto front')
#     ordered_patterns = sorted(patterns, cmp=lambda x,y: subsumLattice.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()),reverse=True)
#   else:
#     ordered_patterns = sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)


#   for pattern in tqdm(ordered_patterns):
#       if pattern in skip_set:
#         # print('skipping the sequence', seq)
#           continue

#       children = set(subsumLattice.get_all_children(pattern))

#       if params['dominance'] == "closed":
#           the_same_sup   = set(support_mapping[pattern.get_support()])
#           prune_patterns = children.intersection(the_same_sup)
#           indices.append(pattern.id)
#       elif params['dominance'] == "maximal":  # simply speaking in case of maximal -- prune the whole subtree
#           prune_patterns = children 
#           indices.append(pattern.id)
#       elif params['dominance'] == "free":
#           the_same_sup   = set(support_mapping[pattern.get_support()])
#           prune_patterns = children.intersection(the_same_sup)
#           prune_patterns.add(pattern)
#           leaves         = subsumLattice.get_leaves(prune_patterns)
#           for leaf in leaves:
#               indices.append(leaf.id)


#       skip_set |= prune_patterns

#   output_patterns = []
#   for p in patterns:
#       if p.id in indices:
#           output_patterns.append(p)
#   return output_patterns


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
    patterns = fpMining_pure(params)
    #for i in range(10):
    #    print patterns[i].get_graphx().nodes(data=False)
    closed_patterns, time_step1, time_step2, time_step3 = fpMining_postpro(params)


    print "\n*************************************"
  # print "Number of frequent patterns: {0}".format(len(patterns))
    print "Number of {0} patterns: {1}".format(params['dominance'], len(closed_patterns))

