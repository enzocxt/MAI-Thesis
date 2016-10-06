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


