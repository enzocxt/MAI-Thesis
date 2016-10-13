import array
import networkx as nx
import sys
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
    def __init__(self, id=None, nsupport=None):
        self.id = id
        self.nsupport = nsupport
        self.parent = -1
        self.graphx = nx.Graph()
        self.coverage = set()

    def set_id(self, id):
        self.id = int(id)

    def set_support(self, support):
        self.nsupport = support

    def get_attributes(self):
      #TODO TO DEBUG!
      print(self.get_nodes())
      nodes = map(lambda x: "v_"+str(x['label']),self.get_nodes())
      edges = map(lambda x: "e_"+str(x['label']),self.get_edges())
      attributes = nodes + edges
      print(attributes)
      return attributes


    def get_nodes(self):
      return self.graphx.nodes(data=True)

    def get_edges(self):
      return self.graphx.edges(data=True)


    def get_number_of_nodes(self):
      return self.graphx.number_of_nodes()

    def get_number_of_edges(self):
      return self.graphx.number_of_edges()

    def add_node(self, v_id, v_label):
        self.graphx.add_node(v_id, label=v_label)

    def add_edge(self, e_from_node, e_to_node, e_label):
        self.graphx.add_edge(e_from_node, e_to_node, label=e_label)

    def build_coverage(self, coverage):
        self.coverage = coverage

    def get_pattern_len(self): # it returns a pair
        return (self.get_number_of_nodes(),self.get_number_of_edges())

    def get_support(self):
        return self.nsupport

    def set_parent(self, parent_id):
        self.parent = int(parent_id)

    def get_parent(self):
        return self.parent

    def get_graphx(self):
        return self.graphx

    def get_attributes(self):
        return self.graphx.nodes(data=False)

    def get_coverage(self):
      return self.coverage

    def has_node(self, node):
        return self.graphx.has_node(node)

    def __str__(self):
        output = 't # {id} * {support}'.format(id=self.id, support=self.nsupport)
        output += '\nparent : {0}'.format(self.parent)
        for v, l in self.graphx.nodes_iter(data='label'):
            output += '\nv {id} {label}'.format(id=v, label=l['label'])
        output += '\n'
        return output

    def has_node(self, node):
        return self.graphx.has_node(node)
    
    @staticmethod
    def _edge_match_(e1,e2):
      return e1['label'] == e2['label']

    @staticmethod
    def _node_match_(v1,v2):
      return v1['label'] == v2['label']


    def is_subgraph_of(self, graph):
      matcher = nx.isomorphism.GraphMatcher(graph.graphx,self.graphx,edge_match=self._edge_match_, node_match=self._node_match_) 
      return matcher.subgraph_is_isomorphic()


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

    def is_subsequence_of(self, seq):
      attr1 = self.get_attributes()
      attr2 = seq.get_attributes()
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
