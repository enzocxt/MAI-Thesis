from collections import defaultdict

"""
The point of this data structure to avoid using the whole dataset in the experiments and IDP code generation
It should split the set of patterns into small groups based on its parameters
"""


def group_by_len(patterns):
  mapping = defaultdict(set)
  for pattern in patterns:
    l = pattern.get_pattern_len()
    mapping[l].add(pattern)
  return mapping

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

def get_attribute_intersection(pattern, mapping, support_mapping):
    first_flag = True
    for attribute in pattern.get_attributes():
        if first_flag:
            patterns_to_check = mapping[attribute]
            first_flag = False
        else:
            patterns_to_check = patterns_to_check.intersection(mapping[attribute])
#   if support_mapping: # if mining closed ones we can make use
#     the_same_support_patterns = support_mapping[pattern.get_pattern_len()]
#   patterns_to_check = patterns_to_check.intersection(the_same_support_patterns)
    return list(patterns_to_check)




