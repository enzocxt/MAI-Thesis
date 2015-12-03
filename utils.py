#!/usr/bin/python

def parser(path):
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
            while 1:
                i += 1
                line = lines[i]
                if 'v' in line:
                    v = line.split(' ')     # v 0 2
                    node = Node()
                    node.id = v[1]
                    node.label = v[2]
                    graph.add_node(node)
                    graphs.append(graph)
                elif 'e' in line:
                    e = line.split(' ')     # e 0 1 0
                    edge = Edge()
                    edge.fromnode = e[1]
                    edge.tonode = e[2]
                    edge.label = e[3]
                    graph.add_edge(edge)
                    graphs.append(graph)
                else:
                    break
            if 't #' not in lines[i]:
                i += 1

        else:
            i += 1

    return graphs
