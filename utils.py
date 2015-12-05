#!/usr/bin/python

from fqPattern import *
from method import *

def parserGraph(path):
    fg = open(path, 'r')
    graphs = []
    lines = fg.readlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if 't #' in line:                   # t # 0 * 45
            t = line.split(' ')
            graph = Graph(t[4])
            graph.id = t[2]
            i += 1
            while i < len(lines):
                line = lines[i]
                if 'v ' in line:
                    v = line.split(' ')     # v 0 2
                    node = Node()
                    node.id = v[1]
                    node.label = v[2]
                    graph.add_node(node)
                    i += 1
                elif 'e ' in line:
                    e = line.split(' ')     # e 0 1 0
                    edge = Edge()
                    edge.fromnode = e[1]
                    edge.tonode = e[2]
                    edge.label = e[3]
                    graph.add_edge(edge)
                    i += 1
                else:
                    break
            graphs.append(graph)
            if i < len(lines) and 't #' not in lines[i]:
                i += 1
            elif i < len(lines) and 't #' in lines[i]:
                continue
        else:
            i += 1

    fg.close()
    return graphs

def parserItemset(path):
    fin = open(path, 'r')
    itemsets = []
    for line in fin.readlines():
        line.rstrip('\n')
        items = line.split(' ')
        if '(' in items[-1]:
            support = items.pop()
            itemset = Itemset(items, support)
            itemsets.append(itemset)
    fin.close()

    return itemsets

def parser(method):
    patterns = None
    if isinstance(method, gSpan):
        patterns = parserGraph(method.output)
    elif isinstance(method, eclat):
        patterns = parserItemset(method.output)

    return patterns
