#from solver.method import prefixSpan#for debugging           
from solver.data_structures import group_by_len, make_attribute_mapping, get_attribute_intersection
from collections import defaultdict
from Pattern import Sequence, Graph

# def main():
#   with open("output/prefix_sequence_user_pos.txt","r") as datafile:
#     data = datafile.read()
#   patterns = prefixSpan.parserSequence(data) 
#   subsumption_tree = create_subsumption_lattice(patterns)
#   print(subsumption_tree)


class SumsumptionLattice:

  def __init__(self, patterns):
    self.lattice = self.create_subsumption_lattice(patterns)

  def create_subsumption_lattice(self, patterns):
    if len(patterns) == 0: return None

    if isinstance(patterns[0], Sequence):
      return self.create_subsumption_lattice_sequence(patterns)
    elif isinstance(patterns[0], Graph):
      return self.create_subsumption_lattice_graph(patterns)

  def create_subsumption_lattice_sequence(self, patterns):
    print('\nCreating subsumption lattice for sequences...')
    subsumption_tree = defaultdict(set)
    mapping_by_len = group_by_len(patterns)
    max_len = max(mapping_by_len.keys())
    attribute_mapping = make_attribute_mapping(patterns)

    for l in range(1,max_len): # maximal are not subsumed by anything
      print('Processing len: %s' % l)
      sequences_with_len_l = mapping_by_len[l]
      for seq in sequences_with_len_l:
        sequences_with_len_l_plus_1 = mapping_by_len[l+1]
        with_at_least_the_same_attributes = get_attribute_intersection(seq, attribute_mapping)
        candidates = sequences_with_len_l_plus_1.intersection(with_at_least_the_same_attributes)
        for candidate in candidates:
          if is_seq1_subsequence_of_seq2(seq.get_attributes(),candidate.get_attributes()):
            subsumption_tree[candidate].add(seq)

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

  def create_subsumption_lattice_graph(self, patterns):
    print('\nCreating subsumption lattice for graphs...')

    subsumption_tree_id = defaultdict(set)  # parent_id: children set
    for graph in patterns:
      subsumption_tree_id[int(graph.get_parent())].add(graph)

    subsumption_tree = defaultdict(set)
    for graph in patterns:
      subsumption_tree[graph] = subsumption_tree_id[int(graph.id)]

    '''
    mapping_by_len = group_by_len(patterns)
    max_len = max(mapping_by_len.keys())
    attribute_mapping = make_attribute_mapping(patterns)

    for l in range(1,max_len): # maximal are not subsumed by anything
      print('Processing len: %s' % l)
      graphs_with_len_l = mapping_by_len[l]
      for graph in graphs_with_len_l:
        graphs_with_len_l_plus_1 = mapping_by_len[l+1]
        with_at_least_the_same_attributes = get_attribute_intersection(graph, attribute_mapping)
        candidates = graphs_with_len_l_plus_1.intersection(with_at_least_the_same_attributes)
        for candidate in candidates:
          if graph.isSubgraph(candidate):
            subsumption_tree[candidate].add(graph)
    '''

    print('Creating subsumption lattice done...\n')
    return subsumption_tree

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
      if is_seq1_subsequence_of_seq2(seq.get_attributes(),transaction_seq.get_attributes()):
        cover_neg.add(seq.id)
    return cover_neg


  def get_leaves(self, patterns, lattice):
    output = []
    for pattern in patterns:
      direct_children = self.get_direct_children(pattern, lattice)
      for child in direct_children:
        if child in patterns:
          break
      else:
        output.append(pattern)
    return output

  def get_all_children(self, pattern, lattice):
    for child in lattice[pattern]:
      yield child
      for indirect_indirect_child in self.get_all_children(child, lattice):
        yield indirect_indirect_child

  def get_direct_children(self, pattern, lattice):
    return lattice[pattern]

  def get_lattice(self):
    return self.lattice

  
# print mapping_by_len
# print attribute_mapping
  
  
def is_seq1_subsequence_of_seq2(attr1, attr2):
  max_l1 = len(attr1)
  max_l2 = len(attr2)
  i = 0
  j = 0
  while i < max_l1:
    if j >= max_l2:
      return False
    if attr1[i] == attr2[j]:
      i += 1
      j += 1
    else:
      j += 1
  return True

if __name__ == "__main__":
  pass
