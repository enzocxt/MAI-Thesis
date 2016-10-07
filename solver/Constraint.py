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

  def generate_vocabulary(self):
    """
    // len vocabulary
    max_len: index
    """
    return '\tmax_len: index\n'

  def generate_theory(self):
    return '\t{\n\tlen_constraint(patternID) <- seq(patternID, index, value) & ~ (?i,v: i >= max_len & seq(patternID,i,v)).\n\t}\n'

  def generate_structure(self):
    return '\tmax_len = {len}\n'.format(len=str(self.max_len))


class IfThenConstraint(Constraint):
  constraint_type = "ifthen"

  def __init__(self, pre, post):
    self.pre = pre
    self.post = post

  def get_pre(self):
    return self.pre

  def get_post(self):
    return self.post

  def generate_vocabulary(self):
    return '\tif:value\n\tthen:value\n'

  def generate_theory(self):
    return '\t{\n\tif_then_constraint(patternID) <- seq(patternID, index, value) & (!i: seq(patternID,i,if) => ?j: seq(patternID,j,then)).\n\t}\n'

  def generate_structure(self):
    return '\tif={pre}\n\tthen={post}\n'.format(pre=self.pre, post=self.post)



class CostConstraint(Constraint):
  constraint_type = "cost"

  def __init__(self, max_cost, cost_mapping):
    self.max_cost = max_cost
    self.cost_mapping = cost_mapping

  def get_max_cost(self):
    return self.max_cost

  def get_cost_mapping(self):
    return self.cost_mapping

  def generate_vocabulary(self):
    return '\tmax_cost: int\n\tcost(value): int\n'

  def generate_theory(self):
    return '\t{\n\tcost_constraint(patternID) <- seq(patternID, index, value) & sum{i, v: seq(patternID,i,v) : cost(v)} < max_cost.\n\t}\n'

  def generate_structure(self):
    costMapping = '{'
    for id, cost in self.cost_mapping.items():
      costMapping += '{id}->{cost};'.format(id=id, cost=cost)
    costMapping = costMapping[:-1] + '}'
    return '\tmax_cost = {maxCost}\n\tcost = {costMapping}\n'.format(maxCost=self.max_cost, costMapping=costMapping)
