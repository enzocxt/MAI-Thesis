import array
import networkx as nx
import sys
"""Pattern classes"""
PLACE_HOLDER = '_'  # for Sequence
from collections import Counter, defaultdict

# Pattern abstract class
class Pattern(object):
    
    stats = defaultdict(int)
    attribute_mapping = defaultdict(set)
    
    id2pattern = {}

    def __init__(self):
        self.id = None
        self.support = None


    def get_pattern_len(self):
        pass


    def get_support(self):
        return self.support


    def __str__(self):
        pass

    def set_stats_and_mapping(self):
      attributes = self.get_attributes()
      for attribute in self.set_of_attributes:
        Pattern.stats[attribute] += 1 
        (Pattern.attribute_mapping[attribute]).add(self)
    
    def get_best_superpattern_set_approximation(self):
      is_first = True
      for attr in self.get_attributes():
        if is_first:
          min_attr = attr
          min_attr_val = Pattern.stats[attr] 
          is_first = False
        else:
          if Pattern.stats[attr] < min_attr_val:
            min_attr = attr
            min_attr_val = Pattern.stats[attr]
      return Pattern.attribute_mapping[min_attr]

    def is_valid(self, constraints):
      for constraint in constraints.values():
        if not constraint.is_valid(self):
          return False
      return True





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
        self.id2pattern = {}
        self.edges = {}
        self.nodes = {}
        self.number_of_nodes = 0
        self.number_of_edges = 0
        self.computed_attributes = False
        self.is_attributes_with_arities_computed = False
        self.all_labeled_counter = None


    def set_id(self, id):
        self.id = int(id)

    def set_support(self, support):
        self.nsupport = support

    def compute_labeled_edges_with_vertices(self):
      labeled = []
      for (e_from,e_to), e_label in self.edges.items():
        labeled.append((self.nodes[e_from],e_label,self.nodes[e_to]))

      self.all_labeled_counter = Counter(labeled)

     
    def get_labeled_edges(self):
        if self.all_labeled_counter is None:
            self.compute_labeled_edges_with_vertices()
        return self.all_labeled_counter

    


    def get_attributes(self):
      #TODO TO DEBUG!
      if self.computed_attributes is False:
          nodes = map(lambda x: "v_"+str(x),self.nodes.values())
          edges = map(lambda x: "e_"+str(x),self.edges.values())
          self.attributes = nodes + edges
          self.computed_attributes = True
          self.set_of_attributes = set(self.attributes)

      return self.attributes

    def get_attributes_with_arities(self):
      if not self.is_attributes_with_arities_computed:
        self.count = Counter(self.get_attributes())
        self.is_attributes_with_arities_computed = True
      return self.count

    def is_superset_by_attributes(self,graph):
      if self.computed_attributes and graph.computed_attributes and not self.set_of_attributes.issuperset(graph.set_of_attributes):
        return False
      counter1 = self.get_attributes_with_arities()
      counter2 = graph.get_attributes_with_arities()
      for key in counter1.keys():
        if counter1[key] < counter2[key]:
          return False
      return True



    def get_number_of_nodes(self):
      return self.number_of_nodes

    def get_number_of_edges(self):
      return self.number_of_edges

    def add_node(self, v_id, v_label):
        self.graphx.add_node(v_id, label=v_label)
        self.nodes[int(v_id)] = int(v_label)
        self.number_of_nodes += 1

    def add_edge(self, e_from_node, e_to_node, e_label):
        self.graphx.add_edge(e_from_node, e_to_node, label=e_label)
        self.edges[(int(e_from_node),int(e_to_node))] = int(e_label)
        self.number_of_edges += 1

    def build_coverage(self, coverage):
        self.coverage = coverage

    def get_pattern_len(self): # it returns a pair
        return (self.number_of_nodes,self.number_of_edges)

    def get_support(self):
        return self.nsupport

    def set_parent(self, parent_id):
        self.parent = int(parent_id)

    def get_parent(self):
        return self.parent

    def get_graphx(self):
        return self.graphx

    def get_coverage(self):
      return self.coverage

    def has_node(self, node):
        return self.graphx.has_node(node)

    def __str__(self):
        output = 't # {id} * {support}'.format(id=self.id, support=self.nsupport)
        output += '\nparent : {0}'.format(self.parent)
        for v, l in self.graphx.nodes_iter(data='label'):
            output += '\nv {id} {label}'.format(id=v, label=l['label'])
        for (e1,e2),l in self.edges.items():
            output += '\ne {e1} {e2} {label}'.format(e1=e1,e2=e2, label=l)

        output += '\n'
        return output

    def is_combined_labeled_supergraph(self, graph):
        counter1 = self.get_labeled_edges()
        counter2 = graph.get_labeled_edges()
        for key in counter1.keys():
            if counter1[key] < counter2[key]:
                return False
        return True



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
        self.attributes = sequence # transform everything to int
        if coverage:
            self.coverage = set(coverage)
        self.support = support
        self.number_of_attributes = len(sequence)
        self.attribute_array = array.array('i', self.attributes)
        self.id2pattern = {}
        self.is_attributes_with_arities_computed = False
        self.set_of_attibutes = set(self.attributes)


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
      output = "id: "+str(self.id) + ' items: '
      for i in self.attribute_array:
          output += '{}'.format(i) + ' '
      output = output[:-1] + ' support :%s' % self.support
      return output

    def __repr__(self):
      return "seq_"+str(self.id)

    def get_support(self):
      return self.support

    def get_attributes(self):
      return self.attributes

    def get_attributes_with_arities(self):
      if not self.is_attributes_with_arities_computed:
        self.count = Counter(self.attributes)
        self.is_attributes_with_arities_computed = True
      return self.count

    def is_superset_by_attributes(self,seq):
      if not self.set_of_attibutes.issuperset(seq.set_of_attibutes):
        return False
      counter1 = self.get_attributes_with_arities()
      counter2 = seq.get_attributes_with_arities()
      for key in counter1.keys():
        if counter1[key] < counter2[key]:
          return False
      return True



    
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
        self.set_of_attributes = self.itemset
        self.attributes = itemset
        self.support = int(support)
        self.size = len(itemset)
        self.id2pattern = {}
        self.min_val = min(itemset)
        self.max_val = max(itemset)
        self.list_of_items = sorted(list(self.itemset))
#       binary = np.zeros(200, dtype=np.int)
#       binary[itemset] = 1
#       self.bitvector = np.packbits(binary)

#   def is_subset(self, itemset):
#       return all(~self.bitvector & itemset.bitvector == 255)
        
    
    def greater_than(self, other_item):
      for i,j in zip(self.list_of_items, other_item.list_of_items):
        if i < j:
          return 1
        elif j > i:
          return -1
      return self.size > other_item.size

    def get_pattern_len(self):
        return self.size

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
        output = [ "id:" + str(self.id) + ' items: ']
        for i in self.itemset:
            output.append(str(i) + ' ')
        output += ' support :%s' % self.support
        return "".join(output)

def add_leadin_zeros(number):
  if number < 9:
    return "00"+str(number)
  if number < 99:
    return "0" +str(number)
  else:
    return str(number)
