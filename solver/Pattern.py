import array
"""Pattern classes"""
PLACE_HOLDER = '_'  # for Sequence

# Pattern abstract class
class Pattern(object):
    def __init__(self):
        self.id = None
        self.support = None


    def get_pattern_len(self):
        pass


    def get_support(self):
        return self.support


    def __str__(self):
        pass


# Edge class for Graph
class Edge(object):
    def __init__(self):
        self.id = None
        self.fromnode = None
        self.tonode = None
        self.label = None


# Node class for Graph
class Node(object):
    def __init__(self):
        self.id = None
        self.label = None
        self.edges = []


class Graph(Pattern):
    def __init__(self, nsupport=None):
        self.id = None
        self.edges = []
        self.nodes = []
        self.nsupport = nsupport
        self.graphx = nx.Graph()

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_pattern_len(self):
        return len(self.nodes)

    def get_support(self):
        return self.nsupport


# Sequence class
class Sequence(Pattern):
    def __init__(self, id=None, sequence=None, support=None, coverage=None):
        #Pattern.__init__()
        self.id = id
        self.sequence = []
        self.attributes = list(map (lambda x: int(x), sequence)) # transform everything to int
        self.coverage = set(coverage)
        for s in sequence:
            self.sequence.append(list(s)) # WHY?
        self.support = support
        self.number_of_attributes = len(sequence)
        self.attribute_array = array.array('i', self.attributes)


    def append(self, p):
        if p.sequence[0][0] == PLACE_HOLDER:
            first_e = p.sequence[0]
            first_e.remove(PLACE_HOLDER)
            self.sequence[-1].extend(first_e)
            self.sequence.extend(p.sequence[1:])
        else:
            self.sequence.extend(p.sequence)
        self.support = min(self.support, p.support)

    def get_coverage(self):
      return self.coverage

    def __str__(self):
        output = str(self.id) + ':'
        for i in self.sequence:
            output += ''.join(i) + ' '
        output = output[:-1] + ':%s' % self.support
        return output

    def __repr__(self):
      return "seq_"+str(self.id)

    def get_support(self):
      return self.support

    def get_attributes(self):
      return self.attributes
    
    def get_pattern_len(self):
      return self.number_of_attributes

    def get_attribute_array(self):
      return self.attribute_array

    def is_identical(self, seq):
      if self.get_pattern_len() != seq.get_pattern_len():
        return False

      for attr1, attr2 in zip(self.get_attributes(), seq.get_attributes()):
        if attr1 != attr2:
          return False

      return True



class Itemset(Pattern):
    def __init__(self, id=None, itemset=None, support=None):
        # Pattern.__init__()
        # self.itemset = itemset
        self.id = id
        self.itemset = set(itemset)
        self.attributes = itemset
        self.support = support
        self.size = len(itemset)

    def get_pattern_len(self):
        return len(self.itemset)

    def get_attributes(self):
        return self.attributes

    def isValid(self):
        pass

    def isClosed(self):
        pass

    def subsetOf(self, itemset):
        if self.size >= itemset.size:
            return False
        for i in range(self.size):
            tmp = self.itemset[i]
            for j in range(itemset.size):
                if tmp == itemset.itemset[j]:
                    break
                else:
                    continue
            if j == itemset.size - 1:
                return False
        return True

    def printItemset(self):
        print self.itemset


    def __str__(self):
        output = str(self.id) + ':'
        for i in self.itemset:
            output += ''.join(i) + ' '
        output = output[:-1] + ':%s' % self.support
        return output
