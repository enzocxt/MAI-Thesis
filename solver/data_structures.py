from collections import defaultdict

"""
The point of this data structure to avoid using the whole dataset in the experiments and IDP code generation
It should split the set of patterns into small groups based on its parameters
"""


def group_by_len(patterns):
  mapping = defaultdict(list)
  for pattern in patterns:
    l = pattern.get_pattern_len()
    mapping[l].append(pattern)
  return mapping



