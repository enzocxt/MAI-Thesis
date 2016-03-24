#!/usr/bin/python

# Pattern abstract class
class Pattern(object):
    def __init__(self):
        self.id = None
        self.support = None


class Edge():
    def __init__(self):
        self.id = None
        self.fromnode = None
        self.tonode = None
        self.label = None

class Node():
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

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)


class Sequence(Pattern):
    def __init__(self, sequence=None):
        Pattern.__init__()
        self.sequence = sequence


class Itemset(Pattern):
    def __init__(self, itemset=None, support=None):
        #Pattern.__init__()
        #self.itemset = itemset
        self.itemset = set(itemset)
        self.support = support
        self.size = len(itemset)

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
                if tmp == itemset.itemset[j]: break
                else: continue
            if j == itemset.size - 1:
                return False
        return True

    def printItemset(self):
        print self.itemset

