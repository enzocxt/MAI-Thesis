#!/usr/bin/python

import time
from fqPattern import *
from method import *

def parserGraph(textOutput, path):
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

def parserItemset(stdOutput, path):
    """
    If path == "" or path == "-",
    means that do not write results into a file
    """
    if path == "" or path == "-":
        result = stdOutput.split('\n')
    else:
        fin = open(path, 'r')
        result = fin.readlines()
        fin.close()
    itemsets = []
    for line in result:
        line.strip('\n')
        items = line.split(' ')
        if not items[0].isdigit():
            continue
        if '(' in items[-1]:
            support = items.pop()
            support = float(support[1:-2])
            itemset = Itemset(items, support)
            itemsets.append(itemset)

    return itemsets

def parser(method, stdOutput, path):
    patterns = None
    if isinstance(method, gSpan):
        patterns = parserGraph(stdOutput, path)
    elif isinstance(method, eclat):
        patterns = parserItemset(stdOutput, path)

    return patterns

def checkClosed(itemset, itemsetList):
    # check if there is a superset of itemset in itemsetList
    for it in itemsetList:
        if itemset.subsetOf(it):
            return False
    return True
