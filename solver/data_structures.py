from collections import defaultdict
from tqdm import tqdm
from itertools import product
MAGIK_NUMBER = 4

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
  for pattern in tqdm(patterns):
    for attribute in pattern.get_attributes():
      mapping[attribute].add(pattern)
  return mapping

def expand_attribute_mapping(mapping, base_mapping):
    new_mapping = {}
    attributes = base_mapping.keys()
    keys = mapping.keys()
    for key in tqdm(keys): 
        for attribute in attributes:
            if isinstance(key,int):
              list_of_key_attributes = [key]
            else:
              list_of_key_attributes = list(key)

            if attribute < max(list_of_key_attributes):
                continue

            list_of_key_attributes.append(attribute)
            new_mapping[tuple(sorted(list_of_key_attributes))] = mapping[key].intersection(base_mapping[attribute])
    return new_mapping

def create_list_of_inverted_mappings(patterns, max_len):
  base_mapping = make_attribute_mapping(patterns)
  map_of_mappings = {1:base_mapping}
  for number_of_attributes in range(2,max_len+1):
    map_of_mappings[number_of_attributes] = expand_attribute_mapping(map_of_mappings[number_of_attributes-1], base_mapping)
  return map_of_mappings

def get_inverted_index(pattern, map_of_mappings, max_len):
  left_items = pattern.get_pattern_len()
  items = sorted(pattern.itemset)
  is_first = True
  max_map  = map_of_mappings[max_len]
  current_index = 0
  while left_items > max_len:
      key = tuple(items[current_index:current_index+max_len])
      if is_first:
          is_first = False
          output   = max_map[key]
      else:
          output   = output.intersection(max_map[key])

      current_index += max_len
      left_items -= max_len

  if left_items > 0:
    key     = tuple(items[current_index:])
    mapping = map_of_mappings[left_items]
    if is_first:
      output = mapping[key]
    else:
      output = output.intersection(mapping[key])

  return output

  


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
      patterns_to_check = patterns_to_check.intersection(the_same_support_patterns)
    return patterns_to_check


def get_attribute_superset(pattern, patternset):
  output = []
  for candidate in patternset:
    if candidate.is_superset_by_attributes(pattern):
      output.append(candidate)
  return output

def get_attribute_subset(pattern, patternset):
  output = []
  for candidate in patternset:
    if pattern.is_superset_by_attributes(candidate):
      output.append(candidate)
  return output



def get_smaller_patterns(min_length, candidates):
   output = []
   for candidate in candidates:
     if candidate.get_pattern_len() < min_length:
       output.append(candidate)
   return output


def check_bounds_and_size(l, min_val, max_val, candidates):
  output = []
  for candidate in candidates:
    if min_val <= candidate.min_val and candidate.max_val <= max_val and candidate.get_pattern_len() < l :
      output.append(candidate)
  return output

def check_larger_and_out_bounds(l, min_val, max_val, candidates):
  output = []
  for candidate in candidates:
    if min_val >= candidate.min_val and candidate.max_val >= max_val and candidate.get_pattern_len() > l :
      output.append(candidate)
  return output



def check_candidate_constraints(candidate, l, min_val, max_val, itemset):
    if min_val <= candidate.min_val and candidate.max_val <= max_val and candidate.get_pattern_len() < l :
      if (candidate.itemset).issubset(itemset.itemset):
        return candidate
      else:
        return None
    else:
      return None


def get_combined_subset(graph, candidates):
  output = []
  for candidate in candidates:
    if graph.is_combined_labeled_supergraph(candidate):
      output.append(candidate)
  return output


