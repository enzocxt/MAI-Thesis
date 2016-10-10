from solver.Pattern import Sequence, Graph

class Constraint:
  constraint_type = "abstract"
  def __init__(self):
    pass


class LengthConstraint(Constraint):
  constraint_type = "length"

  def __init__(self,max_len):
    self.max_len = max_len

  def get_max_length(self):
    return self.max_len

  def is_valid(self, pattern):
    if isinstance(pattern, Sequence):
      return self.is_valid_sequence(pattern)
    elif isinstance(pattern, Graph):
      return self.is_valid_graph(pattern)
    else:
      return True

  def is_valid_sequence(self,seq):
    return seq.get_pattern_len() < self.max_len

  def is_valid_graph(self, graph):
    return graph.get_pattern_len() < self.max_len


class IfThenConstraint(Constraint):
  constraint_type = "ifthen"

  def __init__(self, pre, post):
    self.pre = pre
    self.post = post

  def is_valid(self, pattern):
    if isinstance(pattern, Sequence):
      return self.is_valid_sequence(pattern)
    elif isinstance(pattern, Graph):
      return self.is_valid_graph(pattern)
    else:
      return True

  def is_valid_sequence(self, seq):
    attributes = seq.get_attributes()
    if self.pre in attributes:
      if self.post in attributes:
        return True
      else:
        return False
    else:
      return True

  def is_valid_graph(self, graph):
    if graph.has_node(self.pre):
      return graph.has_node(self.post)
    else:
      return True


class CostConstraint(Constraint):
  constraint_type = "cost"

  def __init__(self, max_cost, cost_mapping):
    self.max_cost = max_cost
    self.cost_mapping = cost_mapping

  def get_max_cost(self):
    return self.max_cost

  def get_cost_mapping(self):
    return self.cost_mapping

  def is_valid(self, pattern):
    if isinstance(pattern, Sequence):
      return self.is_valid_sequence(pattern)
    elif isinstance(pattern, Graph):
      return self.is_valid_graph(pattern)
    else:
      return True

  def is_valid_sequence(self,seq):
    cost = self.get_cost_mapping()
    overall = sum([cost[attr] for attr in seq.get_attributes()])
    return overall <= self.get_max_cost()

  def is_valid_graph(self, graph):
    cost = self.get_cost_mapping()
    overall = sum([cost[attr] for attr in graph.get_attributes()])
    return overall <= self.get_max_cost()

class SequenceLengthConstraint(Constraint):
  constraint_type = "length"
  
  def __init__(self,max_len):
    self.max_len = max_len

  def get_max_length(self):
    return self.max_len

  def is_valid(self,seq):
    return seq.get_pattern_len() < self.max_len


class SequenceIfThenConstraint(Constraint):
  constraint_type = "ifthen"

  def __init__(self, pre, post):
    self.pre = pre
    self.post = post

  def is_valid(self, seq):
    attributes = seq.get_attributes()
    if self.pre in attributes:
      if self.post in attributes:
        return True
      else:
        return False
    else:
      return True

  def get_pre(self):
    return self.pre

  def get_post(self):
    return self.post


class SequenceCostConstraint(Constraint):
  constraint_type = "cost"

  def __init__(self, max_cost, cost_mapping):
    self.max_cost = max_cost
    self.cost_mapping = cost_mapping

  def get_max_cost(self):
    return self.max_cost

  def get_cost_mapping(self):
    return self.cost_mapping

  def is_valid(self,seq):
    cost = self.get_cost_mapping()
    overall = sum([cost[attr] for attr in seq.get_attributes()])
    return overall <= self.get_max_cost()


class GraphLengthConstraint(Constraint):
  constraint_type = "length"

  def __init__(self, max_len):
    self.max_len = max_len

  def get_max_length(self):
    return self.max_len

  def is_valid(self, graph):
    return graph.get_pattern_len() < self.max_len


class GraphIfThenConstraint(Constraint):
  constraint_type = "ifthen"

  def __init__(self, pre_node, post_node):
    self.pre = pre_node
    self.post = post_node

  def is_valid(self, graph):
    if graph.has_node(self.pre):
      return graph.has_node(self.post)
    else:
      return True


class GraphCostConstraint(Constraint):
  constraint_type = "cost"

  def __init__(self, max_cost, cost_mapping):
    self.max_cost = max_cost
    self.cost_mapping = cost_mapping

  def get_max_cost(self):
    return self.max_cost

  def get_cost_mapping(self):
    return self.cost_mapping

  def is_valid(self, graph):
    cost = self.get_cost_mapping()
    overall = sum([cost[attr] for attr in graph.get_nodes()])
    return overall <= self.get_max_cost()
