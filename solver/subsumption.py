  #from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection, get_attribute_superset, get_attribute_subset, make_grouping_by_support, get_smaller_patterns, check_bounds_and_size, check_candidate_constraints, check_larger_and_out_bounds, get_combined_subset
from collections import defaultdict
from Pattern import Itemset, Sequence, Graph, Pattern
from tqdm import tqdm
import sys


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

  def extract_parental_tree_itemset(self, patterns):

    if isinstance(patterns[0], Itemset):
      is_subpattern_of = self.itemset_is_subpattern_of
    elif isinstance(patterns[0], Sequence):
      is_subpattern_of = self.sequence_is_subpattern_of
    pattern_to_parent = defaultdict(set)
    pattern_to_set_of_children = defaultdict(set)
   #for pattern in patterns:
   #  print pattern.list_of_items
    max_upper = len(patterns)
    for i, pattern in tqdm(enumerate(patterns)):
        self.add_pattern_to_the_tree(pattern, patterns, i, pattern_to_parent, pattern_to_set_of_children,max_upper, is_subpattern_of)
    return pattern_to_parent, pattern_to_set_of_children
        
  def add_pattern_to_the_tree(self, pattern, patterns, i, pattern_to_parent, pattern_to_set_of_children, max_upper, is_subpattern_of):
     if isinstance(pattern, Itemset):
        epsilon = 15
     if isinstance(pattern, Sequence):
        epsilon = 10
     upper_bound = min(i+epsilon+1, max_upper)
     lower_bound = max(i-epsilon, 0)
     for j in range (lower_bound, upper_bound):
       if i != j:
        candidate = patterns[j]
        if is_subpattern_of(candidate,pattern):
          pattern_to_parent[pattern].add(candidate)
          pattern_to_set_of_children[candidate].add(pattern)

  def itemset_is_subpattern_of(self,candidate,pattern):
    return (candidate.itemset).issubset(pattern.itemset)
    
  def sequence_is_subpattern_of(self,candidate,pattern):
    return candidate.is_subsequence_of(pattern)
        

  def prune_initial_tree(self, patterns, pattern_to_parent, pattern_to_set_of_children, params):
    skip_set = set()
    for pattern in sorted(patterns, key=lambda x: x.get_pattern_len()):
      if pattern in skip_set:
        continue
      else:
        if params['dominance'] == "maximal":
          subpatterns = pattern_to_parent[pattern]
          for subpattern in subpatterns:
            skip_set.add(subpattern)

        if params['dominance'] == 'closed':
          subpatterns = pattern_to_parent[pattern]
          for subpattern in subpatterns:
            if subpattern.get_support() == pattern.get_support():
              skip_set.add(subpattern)

        if params['dominance'] == 'free':
          superpatterns = pattern_to_set_of_children[pattern]
          for superpattern in superpatterns:
            if superpattern != "root" and superpattern.get_support() == pattern.get_support():
              skip_set.add(superpattern)

    return skip_set




  def subsumption_lattice_check_itemset(self, patterns,params):
    print('\nStarting dominance check for itemsets...')
    
    is_3a_enabled = False
    is_3b_enabled = True 

    all_candidate_sizes = []
    
    is_free = params['dominance'] == "free"
    if is_3a_enabled:
        pattern_to_parent, pattern_to_set_of_children = self.extract_parental_tree_itemset(patterns)
        skip_set = self.prune_initial_tree(patterns, pattern_to_parent, pattern_to_set_of_children, params)

        set_of_patterns = set(patterns) - skip_set


        print('initial skip set size', len(skip_set))
    else:
        set_of_patterns = set(patterns)

    if is_3b_enabled:
        if params['dominance'] == "closed" or is_free:
            support_mapping = make_grouping_by_support(set_of_patterns)

    sorted_itemsets = sorted(set_of_patterns, key=lambda x: x.get_pattern_len(),reverse=(not is_free))
    skip_set = set()
    for itemset in tqdm(sorted_itemsets): # maximal are not subsumed by anything
      if itemset in skip_set:
        continue
      if is_3b_enabled:
          if params['dominance'] == "closed" or is_free:
            candidates = support_mapping[itemset.get_support()] - skip_set
          if params['dominance'] == "maximal":
            candidates = set_of_patterns - skip_set
          

          l = itemset.get_pattern_len()
          if params['dominance'] == "closed" or params['dominance'] == "maximal":
            candidates = check_bounds_and_size(l, itemset.min_val, itemset.max_val, candidates)
          if is_free:
            candidates = check_larger_and_out_bounds(l, itemset.min_val, itemset.max_val, candidates)
      else:
          candidates = (set(patterns) - skip_set) - set([pattern])
      
      all_candidate_sizes.append(len(candidates))
      for candidate in candidates:
        if params['dominance'] == "closed" :
          if not is_3b_enabled and itemset.get_support() != candidate.get_support():
              continue
          if (candidate.itemset).issubset(itemset.itemset): 
                skip_set.add(candidate)

        if params['dominance'] == "maximal": 
          if (candidate.itemset).issubset(itemset.itemset): 
                skip_set.add(candidate)
              
        if is_free:
          if (itemset.itemset).issubset(candidate.itemset):
              skip_set.add(candidate)

#     print("candidates len", len(candidates), "skipset", len(skip_set))
    
    print('Dominance check done...')
    if len(all_candidate_sizes) != 0:
        print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))

    return set_of_patterns - skip_set



  def subsumption_lattice_check_sequence(self, patterns,params):
    print('\n Starting dominance check for sequences...')
    
    
    if params['dominance'] == "maximal":
        pattern_to_parent, pattern_to_set_of_children = self.extract_parental_tree_itemset(patterns)
        skip_set = self.prune_initial_tree(patterns, pattern_to_parent, pattern_to_set_of_children, params)
    else:
        skip_set = set()

    set_of_patterns = set(patterns) - skip_set

    is_free = params['dominance'] == "free"
    if params['dominance'] == "closed" or is_free:
      support_mapping = make_grouping_by_support(set_of_patterns)

    print("initial skip set len", len(skip_set))

    skip_set = set() #init again
    ordered_sequences = sorted(set_of_patterns, key=lambda x: x.get_pattern_len(),reverse=True)

    all_candidate_sizes = []
    for seq in tqdm(ordered_sequences): # maximal are not subsumed by anything
      if seq in skip_set:
        continue
       
      if params['dominance'] == "closed" or is_free:
        candidates = support_mapping[seq.get_support()] - skip_set
      elif params['dominance'] == "maximal":
        candidates = set_of_patterns - skip_set

      candidates = get_smaller_patterns(seq.get_pattern_len(), candidates)
      candidates = get_attribute_subset(seq, candidates)

      all_candidate_sizes.append(len(candidates))

      for candidate in candidates:
        if candidate.is_subsequence_of(seq):
          if (params['dominance'] == "maximal" or params['dominance'] == 'closed'):
                skip_set.add(candidate)

          if params['dominance'] == 'free':
            skip_set.add(seq)
            break

    print('dominance check done')
    if len(all_candidate_sizes) != 0:
        print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))
    return set_of_patterns - set(skip_set)                                               


  def subsumption_lattice_check_graph(self, patterns, params):

    print '\n Starting dominance check for graphs...\n'
   #self.mapping_by_len = group_by_len(patterns)
    initial_subsumption_tree, initial_subsumed_by_tree = self.create_initial_parent_tree(patterns)
    skip_set = self.initialize_skip_set_with_parent_info(patterns, initial_subsumption_tree, initial_subsumed_by_tree, params)
    print("initial skip set", len(skip_set))
    is_free = params['dominance'] == "free"

    set_of_patterns = set(patterns) - skip_set
    sorted_graphs = sorted(set_of_patterns, cmp=lambda x,y: self.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()),reverse=True)

    if params['dominance'] == "closed" or is_free:
      support_mapping = make_grouping_by_support(set_of_patterns)

    skip_set = set()
    all_candidate_sizes = []
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
    return set_of_patterns - skip_set                                               

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
          subpattern_id = subsumed_by.get(pattern.id, -5)
          if subpattern_id != -5 and Graph.id2pattern[subpattern_id] in patterns:
            skip_set.add(pattern)

        if params['dominance'] == 'closed':
          superpattern = subsumed_by.get(pattern.id, -5)
          if superpattern != -5 and Graph.id2pattern[superpattern] in patterns and (Graph.id2pattern[superpattern]).get_support() == pattern.get_support():
            skip_set.add(pattern)

        if params['dominance'] == 'free':
          subpattern = subsumption_tree.get(pattern.id,-5)
          if subpattern != -5 and Graph.id2pattern[subpattern] in patterns and (Graph.id2pattern[subpattern]).get_support() == pattern.get_support(): 
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

