import os, sys
import platform
import subprocess
from tqdm import tqdm
from Pattern import *

# ----------------------------------------------------------
# gSpan command:
# ./gSpan -file [file_name] -support [support: float] &> log

# prefixSpan command:
# Mac OS:
# ./exec/prefixspan [options] dataset
# Linux:
# ./exec/pspan6

# eclat command:
# ./eclat [options] infile [outfile]
# ./eclat -s10 ./output/eclat/zoo-1.txt
# ----------------------------------------------------------

class Mining(object):
    """Abstract class"""

    def __init__(self, inputs):
        # example: inputs{'type': 'itemset', 'matching': 'exact', 'constraints': 'frequency', 'dominance': 'max'}
        self.type = inputs['type']
        if 'matching' in inputs:
            self.matching = inputs['matching']
        else:
            self.matching = None
        if 'constraint' in inputs:
            self.constraint = inputs['constraint']
        else:
            self.constraint = None
        if 'dominance' in inputs:
            self.dominance = inputs['dominance']
        else:
            self.dominance = None
        if 'support' in inputs:
            self.support = float(inputs['support'])
        else:
            self.support = 0.1
        if 'data' in inputs:
            self.data = inputs['data']
        else:
            print 'Need input data file!'
            sys.exit(2)
        if 'output' in inputs:
            self.output = inputs['output']
        else:
            self.output = "-"
        self.patternSet = None

    def mining(self):
        pass

    def parser(self):
        pass


class gSpan(Mining):
    """Use gSpan to mining frequent subgraphs"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)
        Pattern.id2pattern = {}

    def mining(self):
        gSpan_exec = ''
        if platform.system() == "Linux":
            # gSpan = "./exec/gspan"
            gSpan_exec = "./exec/gspan-CT"
        else:
            gSpan_exec = "./exec/gspan"
        options = ''
        if self.support:
            options = ''.join('-support %s' % self.support)

        #child = subprocess.Popen([gSpan, "-f", self.data, "-s", self.support, "-o -i"], stdout=subprocess.PIPE)
        # child = subprocess.Popen([gSpan_exec, "-file", self.data, "-output", self.output, options], shell=False, stderr=devnull)
        command = '{exe} -file {data} -output {output} -support {support} 1> tmp/FNULL'.format(exe=gSpan_exec, data=self.data, output=self.output, support=self.support)
        with open(self.output,"w") as outputfile:
            print(command) #cleaning output
        os.system(command)

        with open(self.output, 'r') as fout:
          print(self.output)
          result = fout.read()

        return result

    def parser(self, stdOutput, path=None):
        self.patternSet = self.parserGraph(stdOutput)
        return self.patternSet

    def parserGraph(self, stdOutput, path=None):
        if path:
            fg = open(path, 'r')
            stdOutput = fg.readlines()
            fg.close()
        return [graph for graph in self.parse_gspan_output(stdOutput)]

    def parse_gspan_output(self, stdOutput):
        data = stdOutput.split('t #')
        for graph_txt in data:
            graph = self.parse_gspan_graph(graph_txt)
            if graph:
                yield graph

    def parse_gspan_graph(self, text):
        if '*' not in text:
            return None
        graph = Graph()
        for line in text.splitlines():
            if '*' in line:
                graph_id, support = line.split('*')
                graph_id = int(graph_id)
                graph.set_id(graph_id)
                Graph.id2pattern[graph_id] = graph
                graph.set_support(int(support))
            if 'parent' in line:
                _, parent_id = line.split(':')
                graph.set_parent(int(parent_id))
            if 'v ' in line:
                _, node_id, node_label = line.split()
                graph.add_node(int(node_id), node_label)
            if 'e ' in line:
                _, edge_from, edge_to, label = line.split()
                graph.add_edge(int(edge_from), int(edge_to), label)
            if 'x ' in line:
                transactions = line.split()
                coverage = set()
                for t in transactions:
                    if 'x' not in t and t != '':
                        coverage.add(int(t))
                graph.build_coverage(coverage)
        graph.set_stats_and_mapping()
        return graph

    def getPatterns(self):
        return self.patternSet


class prefixSpan(Mining):
    """Use prefixSpan to mining frequent sequences"""


    def __init__(self, inputs):
        Mining.__init__(self, inputs)
        Pattern.id2pattern = {}

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        options = ''
        if platform.system() == "Linux" and self.dominance == 'closed':
            prefixSpan = './exec/clospan'
            self.data = self.data.split('.')[0] + '.bin'
            command = '{0} {1} {2} {3}'.format(prefixSpan, self.data, self.support, 10000)
            os.system(command)
            with open('ClosedMaxset.txt', 'r') as seq_out:
                result = seq_out.read()
        elif platform.system() == "Linux":
     #      prefixSpan = "./exec/pspan" # it segfaults on my computer
            prefixSpan = "./exec/prefixspan_linux_64" # compiled for 64bit Linux, tried on Ubuntu 14.04
            if self.support <= 1:
                fin = open(self.data, 'r')
                supp = int(self.support * len(fin.readlines()))
                options += '-min_sup {0}'.format(supp)
            else:
                options += '-S {0}'.format(self.support)
            tmp_output = "tmp/seq_out"
            command = '{0} {1} {2} > {3}'.format(prefixSpan, options, self.data, tmp_output) # MARKER_FOR_LOOKUP
            os.system(command)
            with open(tmp_output,"r") as seq_out:
                result = seq_out.read()
          # child = subprocess.Popen([prefixSpan, options, self.data], stdout=subprocess.PIPE)
        else:
            prefixSpan = "./exec/prefixspan"
            if self.support <= 1:
                fin = open(self.data, 'r')
                supp = int(self.support * len(fin.readlines()))
                #options += '-min_sup {0}'.format(supp)
                options += '-min_sup'
                fin.close()
            else:
                #options += '-min_sup {0}'.format(self.support)
                options += '-min_sup'
            print('Command:\n{0} {1} {2}'.format(prefixSpan, options, self.data))
            command = '{0} {1} {2}'.format(prefixSpan, options, self.data)

            child = subprocess.Popen([prefixSpan, options, str(supp), self.data], stdout=subprocess.PIPE)
            #child = subprocess.Popen([command], stdout=subprocess.PIPE)
            result = child.stdout.read()
            
        return result

    def parser(self, stdOutput, path=None):
        if self.dominance == 'closed':
            self.patternSet = self.parserDomiSequence(stdOutput)
        else:
            self.patternSet = self.parserSequence(stdOutput)
        return self.patternSet
    
    @staticmethod
    def parserSequence(stdOutput, path=None):
        patterns = []
        if path == "" or not path:
            lines = stdOutput.split('\n')
            index = 1
            for i in range(0, len(lines)/2):
                if lines[2*i] == '':
                    continue
                coverage, freq = map(lambda x: x.strip(" ()"), lines[2*i+1].strip().split(':'))
                coverage = map(lambda x: int(x),coverage.split())
                seq = Sequence(index, lines[2*i].strip().split(' '), int(freq), coverage)
                patterns.append(seq) # coverage is the set of transactions covered by the
                Pattern.id2pattern[index] = seq
                index += 1
        else:
            with open(path, 'r') as fin:
                pass
        return patterns

    @staticmethod
    def parserDomiSequence(stdOutput):
        patterns = []
        lines = stdOutput.split('\n')
        index = 1
        for i in range(len(lines)):
            if '<(' not in lines[i]:
                continue
            line = lines[i].strip().split()
            seq = (line[0].replace('<', '').replace('>', '').replace('(', '')).split(')')[:-1]
            seq = Sequence(index, seq, int(line[5]))
            patterns.append(seq)
            Pattern.id2pattern[index] = seq
            index += 1
        return patterns

    def getPatterns(self):
        return self.patternSet


class eclat(Mining):
    """Use eclat to mining frequent itemsets"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)
        self.eclat_exec = None

    def mining(self):
        """Mining frequent itemsets by (closed) eclat"""
        if platform.system() == "Linux":
            self.eclat_exec = "./exec/eclat"
        else:
            self.eclat_exec = "eclat"

        # add options of eclat
        options = ''
        if self.support:
            options += '-s%s' % int(self.support*100)
        if self.dominance == 'max':
            options += 'tm'
        elif self.dominance == 'closed':
            options += 'tc'
        # output absolute item set support
        options += 'v (%a)'

        #tmp_output = "tmp/it_out"
        #command = '{exe} {options} {input} - > {output}'.format(exe=self.eclat_exec, options=options, input=self.data, output=tmp_output)

        child = subprocess.Popen([self.eclat_exec, options, self.data, "-"], stdout=subprocess.PIPE)

        stdOutput = child.stdout.read()
        if self.output == "" or self.output == "-":
            fout = open("output/closed_eclat.txt", 'w')
            fout.write(stdOutput)
            fout.close()
        '''
        os.system(command)
        with open(tmp_output,"r") as it_out:
            stdOutput = it_out.read()
        '''
        return stdOutput

    def parser(self, stdOutput, path=None):
        return [itemset for itemset in self.parserItemset_output(stdOutput)]

    def parserItemset_output(self, stdOutput):
        data = stdOutput.split('\n')
        for i in tqdm(range(len(data))):
            itemset_txt = data[i]
            itemset = self.parserItemset(i, itemset_txt)
            if itemset:
                yield itemset

    def parserItemset(self, index, text):
        line = text.strip()
        items = line.split()
        #print items
        if len(items) == 0 or not items[0].isdigit():
            return None
        if '(' in items[-1]:
            support = items.pop().strip()
            support = int(support[1:-1])
            items = [int(i) for i in items]
            itemset = Itemset(index+1, items, support)
            #itemset.set_stats_and_mapping()
            return itemset

    def parserItemset_old(self, stdOutput, path=None):
        """
            If path == "" or path == "-",
            means that do not write results into a file
        """
        if not path or path == "" or path == "-":
            result = stdOutput.split('\n')
        else:
            fin = open(path, 'r')
            result = fin.readlines()
            fin.close()
        itemsets = []
        for i in tqdm(xrange(len(result))):
            line = result[i]
            line.strip()
            items = line.split(' ')
            if not items[0].isdigit():
              continue
            if '(' in items[-1]:
                support = items.pop().strip()
                # e.g.: 22 32 20 (46)
                support = int(support[1:-1])
                int_items = []
                for x in items:
                    int_items.append(int(x))
                itemset = Itemset(i+1, int_items, support)
                itemset.set_stats_and_mapping()
                itemsets.append(itemset)

        return itemsets

    def maxParser(self, stdOutput):
        """For maximal item sets"""
        pass

    def getPatterns(self):
        return self.patternSet
