from collections import defaultdict

"""
The point of this data structure to avoid using the whole dataset in the experiments and IDP code generation
It should split the set of patterns into small groups based on its parameters
"""

def get_the_same_cover_itemsets(it, itemsets):
    output = set()
    for it2 in itemsets:
        if it.get_support() == it.get_support():
            output.add(it2)
    return output

def get_the_same_cover_sequences(seq, sequences):
  output = set()
  for seq2 in sequences:
    if seq.get_coverage() == seq2.get_coverage():
      output.add(seq2)
  return output

def get_the_same_cover_graphs(graph, graphs):
    output = set()
    for graph2 in graphs:
        if graph.get_coverage() == graph2.get_coverage():
            output.add(graph2)
    return output



def group_by_len(patterns):
  mapping = defaultdict(set)
  for pattern in patterns:
    l = pattern.get_pattern_len()
    mapping[l].add(pattern)
  return mapping

def create_smaller_or_eq_by_len_mapping(len_mapping):
  smaller_or_eq = defaultdict(set)
  for k in len_mapping.keys():
    smaller_or_eq[k] = smaller_or_eq[k-1].union(len_mapping[k]) 
  return smaller_or_eq

def create_greater_or_eq_by_len_mapping_sequences(len_mapping):
  greater_or_eq = defaultdict(set)
  for k in len_mapping.keys():
    greater_or_eq[k] = greater_or_eq[k].union(len_mapping[k+1]) 
  return greater_or_eq

def get_other_smaller_or_eq_patterns(pattern, smaller_or_eq_mapping):
  l = pattern.get_pattern_len()
  other_patterns = smaller_or_eq_mapping[l] - set([pattern])
  return other_patterns

def make_grouping_by_support(patterns):
  mapping = defaultdict(set)
  for pattern in patterns:
    s = pattern.get_support()
    mapping[s].add(pattern)
  return mapping

def make_attribute_mapping(patterns):
  mapping = defaultdict(set)
  for pattern in patterns:
    for attribute in pattern.get_attributes():
      mapping[attribute].add(pattern)
  return mapping


def get_attribute_intersection(pattern, mapping, support_mapping=None):
    first_flag = True
    for attribute in pattern.get_attributes():
        if first_flag:
            patterns_to_check = mapping[attribute]
            first_flag = False
        else:
            patterns_to_check = patterns_to_check.intersection(mapping[attribute])
    if support_mapping: # if mining closed ones we can make use
      the_same_support_patterns = support_mapping[pattern.get_support()]
    if support_mapping: # if mining closed ones we can make use
      the_same_support_patterns = support_mapping[pattern.get_support()]
      patterns_to_check = patterns_to_check.intersection(the_same_support_patterns)
    return patterns_to_check


def get_attribute_superset(pattern, patternset):
  for candidate in patternset:
    if candidate.is_superset_by_attributes(pattern):
      yield candidate

