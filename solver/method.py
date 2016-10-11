import os, sys, time
import platform
import subprocess
import utils
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
        #self.inputs = inputs
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
           #self.data = os.getcwd() + '/' + inputs['data']
            self.data = inputs['data']
            #self.datafile = inputs['datafile']
        else:
            print 'Need input data file!'
            sys.exit(2)
        if 'output' in inputs:
        #   self.output = os.getcwd() + '/' + inputs['output']
            self.output = inputs['output']
        else:
        #    print 'Need specify output file!'
        #    sys.exit(2)
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
        print self.support

        command = '{exe} -file {data} -output {output} -support {support}'.format(exe=gSpan_exec, data=self.data, output=self.output, support=self.support)
        print('%s' % command)
        #child = subprocess.Popen([gSpan, "-f", self.data, "-s", self.support, "-o -i"], stdout=subprocess.PIPE)
        #child = subprocess.Popen(command, stdout=subprocess.PIPE)
        #child = subprocess.Popen([gSpan_exec, "-file", self.data, "-output", self.output, options], stdout=subprocess.PIPE)

        '''
        print([gSpan, "-file", self.data, options])
        child = subprocess.Popen([gSpan, "-file", self.data, options, "&>", self.output], shell=False, stdout=subprocess.PIPE)
        try:
            output = subprocess.check_output([gSpan, "-file", self.datafile, "-output", self.output, options])
            returncode = 0
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode
        '''
        #print(returncode)

        #result = child.stdout.read()
        #result = child.communicate()[0]
        #print result
        #self.parser(result)

        os.system('rm %s' % self.output)
        os.system(command)
        fout = open(self.output, 'r')
        result = fout.read()
        fout.close()

        return result

    def parser(self, stdOutput, path=None):
        self.patternSet = self.parserGraph(stdOutput)
        #self.patternSet = utils.parser(self, stdOutput)
        #self.patternSet = utils.parser(self, None, self.output)
        return self.patternSet

    def parserGraph(self, stdOutput, path=None):
        if not path:
            lines = stdOutput.split('\n')
        else:
            fg = open(path, 'r')
            lines = fg.readlines()
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
                graph.set_id(int(graph_id))
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

        '''
        i = 0
        while i < len(lines):
            line = lines[i]
            if 't' in line:  # t # 0 * 45
                t = line.split()
                graph = Graph(t[2], t[4])     # id, support
                i += 1

                while i < len(lines):
                    line = lines[i]
                    if 'parent' in line:
                        graph.set_parent(int(lines[i].split()[-1]))
                        i += 1
                    elif 'v ' in line:
                        v = line.split(' ')  # v 0 2
                        v_id = v[1]
                        v_label = v[2]
                        graph.add_node(int(v_id), v_label)
                        i += 1
                    elif 'e ' in line:
                        e = line.split()  # e 0 1 0
                        e_from_node = e[1]
                        e_to_node = e[2]
                        e_label = e[3]
                        graph.add_edge(int(e_from_node), int(e_to_node), e_label)
                        i += 1
                    elif 'x' in line:
                        transactions = line.split()
                        coverage = set()
                        for t in transactions:
                            if 'x' not in t and t != '':
                                coverage.add(int(t))
                        graph.build_coverage(coverage)
                        i += 1
                        break
                graphs.append(graph)
                if i < len(lines) and 't' not in lines[i]:
                    i += 1
                elif i < len(lines) and 't' in lines[i]:
                    continue
            else:
                i += 1
        '''
        return graph

    def getPatterns(self):
        return self.patternSet


class prefixSpan(Mining):
    """Use prefixSpan to mining frequent sequences"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        options = ''
        if platform.system() == "Linux":
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
            print(command) 
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
        #stdOutput = stdOutput.split('\n')
        #description, stdOutput = stdOutput[0], stdOutput[1:]
        #if self.support < 1:
        #    self.support = int(description.strip().split(' ')[-1])

        #self.patternSet = utils.parser(self, stdOutput)
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
                patterns.append(Sequence(index, lines[2*i].strip().split(' '), int(freq), coverage)) # coverage is the set of transactions covered by the
                index += 1
        else:
            with open(path, 'r') as fin:
                pass
        return patterns

    def parserSequence_cpsm(self, stdOutput, path=None):
        """
            If path == "" or path == None,
            means that do not write results into a file
        """
        patterns = []
        if path == "" or not path:
            #output = stdOutput.split('\n')
            for i, line in enumerate(stdOutput):
                if 'Pattern' in line:
                    patterns.append(Sequence(i+1, line.split()[2:], self.support))
        else:
            with open(path, 'r') as fin:
                for i, line in enumerate(fin):
                    if 'Pattern' in line:
                        patterns.append(Sequence(i, line.split()[2:], self.support))

        return patterns

    def getPatterns(self):
        return self.patternSet


class prefixSpan_py(Mining):
    """python version of prefixSpan"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        S = utils.read_csv(self.datafile)
        self.patternSet = utils.prefixSpan(S, Sequence([], sys.maxint), self.support)

    def getPatterns(self):
        return self.patternSet

    def print_patterns(self):
        utils.print_patterns(self.patternSet)


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

        #child = subprocess.Popen([self.eclat_exec, options, self.datafile, self.output], stdout=subprocess.PIPE)
        child = subprocess.Popen([self.eclat_exec, options, self.data, "-"], stdout=subprocess.PIPE)

        stdOutput = child.stdout.read()
        if self.output == "" or self.output == "-":
            fout = open("output/closed_eclat.txt", 'w')
            fout.write(stdOutput)
            fout.close()
            #self.patternSet = utils.parser(self, result, "output/closed_eclat.txt")
            #self.patternSet = utils.parser(self, result, "-")
        return stdOutput

    def closedMining(self):
        """
        if mining closed frequent itemsets
        use eclat to find frequent itemset
        and use python post-process to find closed itemsets
        """
        if platform.system() == "Linux":
            eclat = "./exec/eclat"
        else:
            eclat = "eclat"

        child = subprocess.Popen([eclat, "-s%s" % self.support, self.datafile, ""], stdout=subprocess.PIPE)
        result = child.stdout.read()
        if self.dominance == 'max':
            self.maxParser(result)
        elif self.dominance == 'closed':
            closedPatterns = self.closedParser(result)
            return closedPatterns

    def parser(self, stdOutput, path=None):
        self.patternSet = self.parserItemset(stdOutput)
        #self.patternSet = utils.parser(self, None, "output/closed_eclat.txt")
        return self.patternSet

    def parserItemset(self, stdOutput, path=None):
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
        for i, line in enumerate(result):
            line.strip()
            items = line.split(' ')
            if not items[0].isdigit():
                continue
            if '(' in items[-1]:
                support = items.pop().strip()
                # e.g.: 22 32 20 (46)
                support = int(support[1:-1])
                itemset = Itemset(i+1, items, support)
                itemsets.append(itemset)

        return itemsets

    def maxParser(self, stdOutput):
        """For maximal item sets"""
        pass

    def closedParser(self, stdOutput):
        """
        For closed item sets
        Directly check closed itemsets
        Do not store them into python objects,
        and not use objects.method to check closed
        """
        #closedParserTime0 = time.time()
        # itemsets: a dictionary of itemset list
        # itemsets of the same list have same support
        itemsets = {}
        stdOutput = stdOutput.split('\n')
        # pass the description lines
        tmp = stdOutput.pop()
        tmpList = tmp.split()
        while not tmpList[0].isdigit():
            tmp = stdOutput.pop()
            tmpList = tmp.split(' ')
        stdOutput.append(tmp)

        for line in stdOutput:
            line.strip('\n')
            items = line.split(' ')
            support = items.pop()
            support = float(support[1:-1])
            itemset = (support, set(items))

            # if itemsets dictionary has support of this itemset
            # add this itemset to that list
            # else add this itemset as a new itemset list
            if itemsets.has_key(itemset[0]):
                itemsets[itemset[0]].append(itemset[1])
            else:
                itemsets[itemset[0]] = [itemset[1]]

        def checkClosed(itemset, itemsetList):
            for it in itemsetList:
                if len(itemset) >= len(it):
                    continue
                elif itemset < it:
                    return False
            return True

        # find closed itemset
        closedItemset = []
        for list in itemsets.values():
            for i in range(len(list)):
                if checkClosed(list[i], list):
                    closedItemset.append(list[i])

        return closedItemset

    def getPatterns(self):
        return self.patternSet
