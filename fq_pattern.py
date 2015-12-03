#!/usr/bin/python

class Pattern(object):
    def __init__(self):
        self.id = None

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

class Graph():
    def __init__(self, nsupport=None):
        self.id = None
        self.edges = []
        self.nodes = []
        self.nsupport = nsupport

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

