  #from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection, get_attribute_superset, get_attribute_subset, make_grouping_by_support, get_smaller_patterns, check_bounds_and_size, check_candidate_constraints, check_larger_and_out_bounds, get_combined_subset
from collections import defaultdict
from Pattern import Itemset, Sequence, Graph, Pattern
from tqdm import tqdm
import sys
import numpy as np


class SubsumptionLattice:

  # currently not used anywhere
  MAGIC_NUMBER = 4 # upper bound for early stopping of local constraint check, if local group is smaller then this, goto direct constraint validation
                   

  def __init__(self):
    pass

  def check_dominance(self, patterns, params):
    if len(patterns) == 0: return None

    if isinstance(patterns[0], Itemset):
      return self.subsumption_lattice_check_itemset(patterns,params)
    elif isinstance(patterns[0], Sequence):
      return self.subsumption_lattice_check_sequence(patterns,params)
    elif isinstance(patterns[0], Graph):
      return self.subsumption_lattice_check_graph(patterns,params)

  def subsumption_lattice_check_itemset(self, patterns,params):
    print('\nStarting dominance check for itemsets...')
    
    check = np.vectorize(check_candidate_constraints)

    is_free = params['dominance'] == "free"
    if params['dominance'] == "closed" or is_free:
      support_mapping = make_grouping_by_support(patterns)

    skip_set = set()
    all_candidate_sizes = []
   #map_of_maps = create_list_of_inverted_mappings(patterns, 3)
    sorted_itemsets = sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=(not is_free))
    for itemset in tqdm(sorted_itemsets): # maximal are not subsumed by anything
      if itemset in skip_set:
        continue
      
      if params['dominance'] == "closed" or is_free:
        candidates = support_mapping[itemset.get_support()] - skip_set
      if params['dominance'] == "maximal":
        candidates = set(patterns) - skip_set

      l = itemset.get_pattern_len()
      if params['dominance'] == "closed" or params['dominance'] == "maximal":
        candidates = check_bounds_and_size(l, itemset.min_val, itemset.max_val, candidates)
      if is_free:
        candidates = check_larger_and_out_bounds(l, itemset.min_val, itemset.max_val, candidates)

      for candidate in candidates:
        if params['dominance'] == "closed" or params['dominance'] == "maximal":
          if (candidate.itemset).issubset(itemset.itemset):
              skip_set.add(candidate)
        if is_free:
          if (itemset.itemset).issubset(candidate.itemset):
              skip_set.add(candidate)

#     print("candidates len", len(candidates), "skipset", len(skip_set))
    
    print('Dominance check done...')
    if len(all_candidate_sizes) != 0:
        print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))

    return set(patterns) - skip_set


  def subsumption_lattice_check_sequence(self, patterns,params):
    print('\n Starting dominance check for sequences...')
    mapping_by_len = group_by_len(patterns)
    max_len = max(mapping_by_len.keys())
    skip_set = set()
    all_candidate_sizes = []
    
    ordered_sequences = sorted(patterns, key=lambda x: x.get_pattern_len(),reverse=True)
    for seq in tqdm(ordered_sequences): # maximal are not subsumed by anything
      if seq in skip_set:
        continue

      
      candidates = set(patterns) - skip_set
      candidates = get_smaller_patterns(seq.get_pattern_len(), candidates)
      candidates = get_attribute_subset(seq, candidates)
      all_candidate_sizes.append(len(candidates))

      for candidate in candidates:
        if candidate.is_subsequence_of(seq):
          if params['dominance'] == "maximal" or params['dominance'] == 'closed':
            skip_set.add(candidate)

          if params['dominance'] == 'free':
            skip_set.add(seq)
            break

    print('dominance check done')
    if len(all_candidate_sizes) != 0:
        print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))
    return set(patterns) - set(skip_set)                                               

  def subsumption_lattice_check_graph(self, patterns, params):
    print '\n Starting dominance check for graphs...\n'
   #self.mapping_by_len = group_by_len(patterns)
    
    initial_subsumption_tree, initial_subsumed_by_tree = self.create_initial_parent_tree(patterns)
    skip_set = self.initialize_skip_set_with_parent_info(patterns, initial_subsumption_tree, initial_subsumed_by_tree, params)
    print("initial skip set", len(skip_set))
    all_candidate_sizes = []
    is_free = params['dominance'] == "free"
    if params['dominance'] == "closed" or is_free:
      support_mapping = make_grouping_by_support(patterns)
    #TODO rewrite free dominance part or should I leave it like that? probably can be optimized
    sorted_graphs = sorted(patterns, cmp=lambda x,y: self.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()),reverse=True)
    for graph in tqdm(sorted_graphs): # maximal are not subsumed by anything
      if graph in skip_set:
          continue
        
      if params['dominance'] == "closed" or is_free:
        candidates = support_mapping[graph.get_support()] - skip_set
      if params['dominance'] == "maximal":
        candidates = set(patterns) - skip_set

      candidates = filter(lambda x: self.pareto_front_pair(x.get_pattern_len(),graph.get_pattern_len()) < 0, candidates)
      candidates = get_attribute_subset(graph, candidates)
      candidates = get_combined_subset(graph, candidates)

      number_of_candidates = len(candidates)
      all_candidate_sizes.append(number_of_candidates)

      for candidate in candidates:
          if candidate.is_subgraph_of(graph):
            if params['dominance'] == "maximal" or params['dominance'] == 'closed':
              skip_set.add(candidate)

            if params['dominance'] == 'free':
              skip_set.add(graph)
              break


    print 'done dominance check'
    print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))
    return set(patterns) - set(skip_set)                                               

  @staticmethod
  def create_initial_parent_tree(patterns):
    initial_subsumption_tree = {}
    initial_subsumed_by_tree = {}
    for pattern in patterns:
        if pattern.parent == -1:
            continue
      
        initial_subsumption_tree[pattern.id] = int(pattern.parent)
        initial_subsumed_by_tree[pattern.parent] = int(pattern.id)


    return initial_subsumption_tree, initial_subsumed_by_tree

  @staticmethod
  def get_all_initial_descendants(pattern, initial_subsumed_by_tree):
    parents = []
    current_id = pattern.id
    while True:
      current_parent = initial_subsumed_by_tree.get(current_id, -5)
      if current_parent == -5:
        return parents
      else:
        current_id = current_parent
        parents.append(current_id)

  def initialize_skip_set_with_parent_info(self, patterns, subsumption_tree, subsumed_by, params):

    skip_set = set()
    for pattern in sorted(patterns, cmp=lambda x,y: self.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()), reverse=True):
      if pattern in skip_set:
        continue
      else:
        if params['dominance'] == "maximal":
          if subsumed_by.get(pattern.id, -5) != -5:
            skip_set.add(pattern)

        if params['dominance'] == 'closed':
          superpattern = subsumed_by.get(pattern.id, -5)
          if superpattern != -5 and (Graph.id2pattern[superpattern]).get_support() == pattern.get_support():
            skip_set.add(pattern)

        if params['dominance'] == 'free':
          subpattern = subsumption_tree.get(pattern.id,-5)
          if subpattern != -5 and (Graph.id2pattern[subpattern]).get_support() == pattern.get_support(): 
            skip_set.add(pattern)

    return skip_set

  def apply_extra_dominance_constraints(self, pattern, candidates, params):
      output = []
      if params['dominance'] == "maximal":
        return candidates
      if params['dominance'] == 'closed' or params['dominance'] == 'free':
        for candidate in candidates:
          if pattern.get_support() == candidate.get_support():
            output.append(candidate)
      return output
                                                                          
                                                                          
  @staticmethod                                                         
  def pareto_front_pair(x,y):                                             
    if x == y: return 0                                                   
    if x[0] >= y[0] and x[1] >= y[1]: return 1                            
    else: return -1                                                       
                                                                          
  def get_all_parents(self,pattern, subsumed_by):
    for parent in subsumed_by[pattern]:
      yield parent
      for indirect_parent in self.get_all_parents(parent,subsumed_by):
        yield indirect_parent

                                                                          
  def read_negative_dataset_sequences(self, params):
    filename = params['negative']
    with open(filename,"r") as negativefile:
      lines = negativefile.read().splitlines()
    sequences = [map(lambda x: int(x), line.split()) for line in lines]
    output = []
    for i,seq in enumerate(sequences):
      output.append(Sequence(id=i,sequence=seq))
    return output

  def compute_sequence_coverage(self, seq, in_sequences):
    cover_neg = set()
    for transaction_seq in in_sequences:
      if seq.is_subsequence_of(transaction_seq):
        cover_neg.add(seq.id)
    return cover_neg

  def get_leaves(self, patterns, lattice=None):
    output = []
    for pattern in patterns:
      direct_children = self.get_direct_children(pattern)
      for child in direct_children:
        if child in patterns:
          break
      else:
        output.append(pattern)
    return output

  def get_all_children(self, pattern):
    for child in self.lattice[pattern]:
      yield child
      for indirect_indirect_child in self.get_all_children(child):
        yield indirect_indirect_child

  def get_direct_children(self, pattern):
    return self.lattice[pattern]

