#from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection, get_attribute_superset
from collections import defaultdict
from Pattern import Itemset, Sequence, Graph
from tqdm import tqdm


class SubsumptionLattice:

  MAGIC_NUMBER = 4 # upper bound for early stopping of local constraint check, if local group is smaller then this, goto direct constraint validation

  def __init__(self):
    pass

  def check_dominance(self, patterns, params):
    if len(patterns) == 0: return None

    if isinstance(patterns[0], Itemset):
      return self.create_subsumption_lattice_itemset(patterns)
    elif isinstance(patterns[0], Sequence):
      return self.create_subsumption_lattice_sequence(patterns,params)
    elif isinstance(patterns[0], Graph):
      return self.create_subsumption_lattice_graph(patterns,params)

  #TODO check and rewrite -- Sergey, modified a bit
  def create_subsumption_lattice_itemset(self, patterns):
    print('\nCreating subsumption lattice for itemsets...')
    subsumption_tree = defaultdict(set)
    mapping_by_len = group_by_len(patterns)
    max_len = max(mapping_by_len.keys())
    attribute_mapping = make_attribute_mapping(patterns)

    for l in range(1, max_len):
   #  print('Processing len: %s' % l)
      itemsets_with_len_l = mapping_by_len[l]
      for it in itemsets_with_len_l:
        candidates = filter(lambda x: x.get_pattern_len() > l, get_attribute_intersection(it, attribute_mapping))
        for candidate in candidates:
            subsumption_tree[candidate].add(it)

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

  def get_larger_sequences(self, min_length, candidates):
    output = []
    for candidate in candidates:
      if candidate.get_pattern_len() > min_length:
        output.append(candidate)
    return output

  def create_subsumption_lattice_sequence(self, patterns,params):
    print('\n Starting dominance check for sequences...')
    mapping_by_len = group_by_len(patterns)
#   attribute_mapping = make_attribute_mapping(patterns)
    max_len = max(mapping_by_len.keys())
    skip_set = set()
    all_candidate_sizes = []

    for l in tqdm(range(1,max_len)): # maximal are not subsumed by anything
 #    print('Processing len: %s' % l)
      sequences_with_len_l = mapping_by_len[l]
      for seq in sequences_with_len_l:
        if seq in skip_set:
          continue

        candidates = set(patterns) - skip_set
        candidates = self.get_larger_sequences(l, candidates)
        candidates = get_attribute_superset(seq, candidates)
        candidates = self.apply_extra_dominance_constraints(seq, candidates, params)
        all_candidate_sizes.append(len(candidates))

        for candidate in candidates:
          if seq.is_subsequence_of(candidate):
            if params['dominance'] == "maximal" or params['dominance'] == 'closed':
              skip_set.add(seq)
              break

            if params['dominance'] == 'free':
              skip_set.add(candidate)

    print('dominance check done')
    if len(all_candidate_sizes) != 0:
        print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))
    return set(patterns) - set(skip_set)                                               

  
  def create_subsumption_lattice_graph(self, patterns, params):
    print '\n Starting dominance check \n'
    self.mapping_by_len = group_by_len(patterns)
  # attribute_mapping = make_attribute_mapping(patterns)

    
    initial_subsumption_tree, initial_subsumed_by_tree = self.create_initial_parent_tree(patterns)
    skip_set = self.initialize_skip_set_with_parent_info(patterns, initial_subsumption_tree, initial_subsumed_by_tree, params)
    print("initial skip set", len(skip_set))
    all_candidate_sizes = []
    different_lenghts = sorted(self.mapping_by_len.keys(), cmp=self.pareto_front_pair,reverse=True)
    for l in tqdm(different_lenghts): # maximal are not subsumed by anything
        graphs_with_len_l = self.mapping_by_len[l]
        for graph in graphs_with_len_l:
          if graph in skip_set:
            continue

          candidates = set(patterns) - skip_set
          candidates = filter(lambda x: self.pareto_front_pair(x.get_pattern_len(),graph.get_pattern_len()) > 0, candidates)
          candidates = get_attribute_superset(graph, candidates)
          candidates = self.apply_extra_dominance_constraints(graph,candidates, params)
        # candidates = get_attribute_intersection(graph, attribute_mapping) - skip_set

          all_candidate_sizes.append(len(candidates))

          sorted_candidates = sorted(candidates, cmp=lambda x,y: self.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()))

          for candidate in sorted_candidates:
                     
              if graph.is_subgraph_of(candidate):
                if params['dominance'] == "maximal" or params['dominance'] == 'closed':
                  skip_set.add(graph)
                  break

                if params['dominance'] == 'free':
                  skip_set.add(candidate)


    print 'done dominance check'                                                                   
    print 'AVG candidate size:', float(sum(all_candidate_sizes))/float(len(all_candidate_sizes))
    return set(patterns) - set(skip_set)                                               

  def get_all_parents(self,pattern, subsumed_by):
    for parent in subsumed_by[pattern]:
      yield parent
      for indirect_parent in self.get_all_parents(parent,subsumed_by):
        yield indirect_parent

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
          if subpattern != -5 or (Graph.id2pattern[subpattern]).get_support() == pattern.get_support(): 
            skip_set.add(pattern)

    return skip_set

  def apply_extra_dominance_constraints(self, graph, candidates, params):
      output = []
      if params['dominance'] == "maximal":
        return candidates
      if params['dominance'] == 'closed' or params['dominance'] == 'free':
        for pattern in candidates:
          if graph.get_support() == pattern.get_support():
            output.append(pattern)
      return output
      

                                                                          
                                                                          
                                                                          
  @staticmethod                                                         
  def pareto_front_pair(x,y):                                             
    if x == y: return 0                                                   
    if x[0] >= y[0] and x[1] >= y[1]: return 1                            
    else: return -1                                                       
                                                                          
                                                                          
                                                                          
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

  def get_lattice(self):
    return self.lattice

  
# print mapping_by_len
# print attribute_mapping

if __name__ == "__main__":
  pass
