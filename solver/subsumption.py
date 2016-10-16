#from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection, get_attribute_superset
from collections import defaultdict
from Pattern import Itemset, Sequence, Graph
from tqdm import tqdm

# def main():
#   with open("output/prefix_sequence_user_pos.txt","r") as datafile:
#     data = datafile.read()
#   patterns = prefixSpan.parserSequence(data) 
#   subsumption_tree = create_subsumption_lattice(patterns)
#   print(subsumption_tree)


class SubsumptionLattice:

  def __init__(self, patterns):
    self.lattice = self.create_subsumption_lattice(patterns)

  def create_subsumption_lattice(self, patterns):
    if len(patterns) == 0: return None

    if isinstance(patterns[0], Itemset):
      return self.create_subsumption_lattice_itemset(patterns)
    elif isinstance(patterns[0], Sequence):
      return self.create_subsumption_lattice_sequence(patterns)
    elif isinstance(patterns[0], Graph):
      return self.create_subsumption_lattice_graph(patterns)

  #TODO check and rewrite -- Sergey, modified a bit
  def create_subsumption_lattice_itemset(self, patterns):
    print('\nCreating subsumption lattice for itemsets...')
    subsumption_tree = defaultdict(set)
    mapping_by_len = group_by_len(patterns)
    max_len = max(mapping_by_len.keys())
    attribute_mapping = make_attribute_mapping(patterns)

    for l in range(1, max_len):
      print('Processing len: %s' % l)
      itemsets_with_len_l = mapping_by_len[l]
      for it in itemsets_with_len_l:
        candidates = filter(lambda x: x.get_pattern_len() > l, get_attribute_intersection(it, attribute_mapping))
        for candidate in candidates:
            subsumption_tree[candidate].add(it)

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

  def create_subsumption_lattice_sequence(self, patterns):
    print('\nCreating subsumption lattice for sequences...')
    subsumption_tree = defaultdict(set)

    self.mapping_by_len = group_by_len(patterns)
    max_len = max(self.mapping_by_len.keys())
    self.attribute_mapping = make_attribute_mapping(patterns)

    for l in range(1,max_len): # maximal are not subsumed by anything
      print('Processing len: %s' % l)
      sequences_with_len_l = self.mapping_by_len[l]
      for seq in sequences_with_len_l:
        candidates = filter(lambda x: x.get_pattern_len() > l, get_attribute_intersection(seq, self.attribute_mapping))
        for candidate in candidates:
          if seq.is_subsequence_of(candidate):
            subsumption_tree[candidate].add(seq)

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

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
      
        initial_subsumption_tree[pattern.id] = pattern.parent  
        initial_subsumed_by_tree[pattern.parent] = pattern.id

    return initial_subsumed_by_tree

  @staticmethod
  def get_all_initial_descendants(pattern, initial_subsumed_by_tree):
    parents = []
    current_id = pattern.id
    while True:
      current_parent = initial_subsumed_by_tree.get(current_id, -5)
      if current_parent == -5:
        return parents
      else:
        current_id = current_parent.id
        parents.append(current_id)


   


  def create_subsumption_lattice_graph(self, patterns):
    print('\nCreating subsumption lattice for graphs...')

    self.mapping_by_len = group_by_len(patterns)
    self.attribute_mapping = make_attribute_mapping(patterns)

    subsumed_by = defaultdict(list)
    subsumption_tree = defaultdict(set)
    
    initial_parent_subsumed_by_tree = self.create_initial_parent_tree(patterns)


    for l in tqdm(sorted(self.mapping_by_len.keys(), cmp=self.pareto_front_pair,reverse=True)): # maximal are not subsumed by anything
        print('Processing graph of size = {size}'.format(size=l))
        # PARALELLIZATION_MARKER for different graphs of the same len
        graphs_with_len_l = self.mapping_by_len[l]
        print('we have l graphs with len l', len(graphs_with_len_l))
        for graph in graphs_with_len_l:
        #  print("attribute interstionction started")
           candidates = filter(lambda x: self.pareto_front_pair(x.get_pattern_len(),graph.get_pattern_len()) > 0, get_attribute_intersection(graph, self.attribute_mapping))
           candidates = list(get_attribute_superset(graph, candidates))
         # print("attribute interstionction done")
         # print("candidates setsize", len(candidates))
           skip_set   = set()
           all_descendants = self.get_all_initial_descendants(graph, initial_parent_subsumed_by_tree)
           print("initial descendants len", len(all_descendants))
           sorted_candidates = sorted(candidates, cmp=lambda x,y: self.pareto_front_pair(x.get_pattern_len(),y.get_pattern_len()))
           for candidate in sorted_candidates:

               if candidate in skip_set:
                   continue
                      
               if candidate.id in all_descendants or graph.is_subgraph_of(candidate):
                   subsumed_by[graph].append(candidate)
                   subsumption_tree[candidate].add(graph)
                   parents = set(self.get_all_parents(candidate,subsumed_by))
                   skip_set |= parents

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

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
