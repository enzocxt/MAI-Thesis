import networkx as nx

def main():
    [graph for graph in parse_gspan_output("tmp/gspan_test_output.txt")]


def parse_graph(text):
    if "*" not in text: # if it is an empty string, return nothing
        return None
    G = nx.Graph()
    for line in text.splitlines():
        if "*" in line:
            graph_id, coverage = line.split("*")
            G.graph['id'], G.graph['support'] = int(graph_id), int(coverage)
        if "v " in line:
            _, node_id, node_label = line.split(" ")
            #TODO add it to networkx graph
            print('node_id,node_label',node_id,node_label)
        if "e " in line:
            _, edge_from, edge_to, label = line.split(" ")
            print('edge: from, to, label', edge_from, edge_to, label)
        if "x:" in line:
            coverage = line.split(" ") # remove the first marker "x:"
            print('coverage:', coverage)
        if "parent" in line: #TODO handle this graph, possibly reify
            _, parent_id = line.split(":")
      
    

def parse_gspan_output(filepath):
    with open(filepath,"r") as datafile:
        data = datafile.read().split("t #")
        for graph_txt in data:
            graph = parse_graph(graph_txt)
            if graph:
                yield graph





if __name__ == "__main__":
    main()
