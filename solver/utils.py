import time
from fqPattern import *
from method import *

PLACE_HOLDER = '_'

def parserGraph(stdOutput, path=None):
    if not path:
        lines = stdOutput.split('\n')
    else:
        fg = open(path, 'r')
        lines = fg.readlines()
        fg.close()
    graphs = []
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

def parser(method, stdOutput, path=None):
    patterns = None
    if isinstance(method, gSpan):
        patterns = parserGraph(stdOutput, path)
    elif isinstance(method, eclat):
        patterns = parserItemset(stdOutput, path)

    return patterns

def checkClosed(itemset, itemsetList):
    # check if there is a superset of itemset in itemsetList
    for it in itemsetList:
        if itemset.size >= it.size:
            continue
        #if itemset.subsetOf(it):
        elif itemset.itemset < it.itemset:
            return False
    return True


# ---------------------------prefixSpan------------------------------

def frequent_items(S, pattern, threshold):
    items = {}
    _items = {}
    f_list = []
    if S is None or len(S) == 0:
        return []
    if len(pattern.sequence) != 0:
        last_e = pattern.sequence[-1]
    else:
        last_e = []
    for s in S:
        # 1
        is_prefix = True
        for item in last_e:
            if item not in s[0]:
                is_prefix = False
                break
        if is_prefix and len(last_e) > 0:
            index = s[0].index(last_e[-1])
            if index < len(s[0])-1:
                for item in s[0][index+1:]:
                    if item in _items:
                        _items[item] += 1
                    else:
                        _items[item] = 1
        # 2
        if PLACE_HOLDER in s[0]:
            for item in s[0][1:]:
                if item in _items:
                    _items[item] += 1
                else:
                    _items[item] = 1
            s = s[1:]
        # 3
        counted = []
        for element in s:
            for item in element:
                if item not in counted:
                    counted.append(item)
                    if item in items:
                        items[item] += 1
                    else:
                        items[item] = 1

    f_list.extend([SquencePattern([[PLACE_HOLDER, k]], v)
                   for k, v in _items.iteritems()
                   if v >= threshold])
    f_list.extend([SquencePattern([[k]], v)
                   for k, v in items.iteritems()
                   if v >= threshold])
    sorted_list = sorted(f_list, key=lambda p: p.support)
    return sorted_list

def build_projected_database(S, pattern):
    """
    supporse S is projected database based on pattern's prefix,
    so we only need to use the last element in pattern to
    build projected database
    """
    p_S = []
    last_e = pattern.sequence[-1]
    last_item = last_e[-1]
    for s in S:
        p_s = []
        for element in s:
            is_prefix = False
            if PLACE_HOLDER in element:
                if last_item in element and len(pattern.sequence[-1]) > 1:
                    is_prefix = True
            else:
                is_prefix = True
                for item in last_e:
                    if item not in element:
                        is_prefix = False
                        break

            if is_prefix:
                e_index = s.index(element)
                i_ind    = element.index(last_item)
                if i_index == len(element) - 1:
                    p_s = s[e_index+1:]
                else:
                    p_s = s[e_index:]
                    index = element.index(last_item)
                    e = element[i_index:]
                    e[0] = PLACE_HOLDER
                    p_s[0] = e
                break
        if len(p_s) != 0:
            p_S.append(p_s)

    return p_S

def prefixSpan(pattern, S, threshold):
    patterns = []
    f_list = frequent_items(S, pattern, threshold)

    for i in f_list:
        p = SquencePattern(pattern.sequence, pattern.support)
        p.append(i)
        patterns.append(p)

        p_S = build_projected_database(S, p)
        p_patterns = prefixSpan(p, p_S, threshold)
        patterns.extend(p_patterns)

    return patterns

# -------------------------------------------------------------------
