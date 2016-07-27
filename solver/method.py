import os, sys, time
import platform
import subprocess
import utils
from Pattern import *

# ----------------------------------------------------------
# gSpan command:
# ./gSpan -file [file_name] -support [support: float] &> log

# prefixSpan command:
# ./exec/cpsm [options] [[dataset] [minimum frequency threshold]]

# eclat command:
# ./eclat [options] infile [outfile]
# ----------------------------------------------------------

class Mining(object):
    """Abstract class"""

    def __init__(self, inputs):
        # example: inputs{'type': 'itemset', 'matching': 'exact', 'constraints': 'frequency', 'dominance': 'max'}
        #self.inputs = inputs
        self.type = inputs['type']
        if inputs.has_key('matching'): self.matching = inputs['matching']
        else: self.matching = None
        if inputs.has_key('constraint'): self.constraint = inputs['constraint']
        else: self.constraint = None
        if inputs.has_key('dominance'): self.dominance = inputs['dominance']
        else: self.dominance = None
        if inputs.has_key('support'): self.support = inputs['support']
        else: self.support = None
        if inputs.has_key('datafile'):
            self.datafile = os.getcwd() + '/' + inputs['datafile']
            #self.datafile = inputs['datafile']
        else:
            print 'Need input data file!'
            sys.exit(2)
        if inputs.has_key('output'):
            self.output = os.getcwd() + '/' + inputs['output']
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
        if platform.system() == "Linux":
            gSpan = "/home/enzo/Thesis/MAI-Thesis/exec/gspan"
        else:
            gSpan = "gspan"
        options = ''
        if self.support:
            options = ''.join('-support %s' % self.support)

        #print("%s -file %s %s" % (gSpan, self.datafile, options))
        print([gSpan, "-file", self.datafile, options])
        child = subprocess.Popen([gSpan, "-file", self.datafile, options, "&> ", self.output], shell=False, stdout=subprocess.PIPE)
        try:
            output = subprocess.check_output([gSpan, "-file", self.datafile, options])
            returncode = 0
        except subprocess.CalledProcessError as e:
            output = e.output
            returncode = e.returncode
        print(output)
        print(returncode)

        #result = child.stdout.read()
        result = child.communicate()[0]
        print result
        #self.parser(result)
        #fout = open(self.output, 'w')
        #fout.write(result)
        #fout.close()
        return result

    def parser(self, stdOutput, path=None):
        self.patternSet = utils.parser(self, stdOutput)
        self.patternSet = utils.parser(self, None, self.output)
        return self.patternSet

    def getPatterns(self):
        return self.patternSet


class prefixSpan(Mining):
    """Use prefixSpan to mining frequent sequences"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent sequences by prefixSpan"""
        if platform.system() == "Linux":
            prefixSpan = "./exec/cpsm"
        else:
            prefixSpan = "prefixSpan"
        options = ''

        child = subprocess.Popen([prefixSpan, options, self.datafile, ''.join(self.support)], stdout=subprocess.PIPE)
        result = child.communicate()[0]
        return result

    def parser(self, stdOutput, path=None):
        self.patternSet = utils.parser(self, stdOutput)
        return self.patternSet

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

        options = ''
        if self.support:
            options += '-s%s' % self.support
        if self.dominance == 'max':
            options += 'tm'
        elif self.dominance == 'closed':
            options += 'tc'

        # check time cost
        t0 = time.time()
        #child = subprocess.Popen([self.eclat_exec, options, self.datafile, self.output], stdout=subprocess.PIPE)
        child = subprocess.Popen([self.eclat_exec, options, self.datafile, "-"], stdout=subprocess.PIPE)
        t1 = time.time()

        result = child.stdout.read()
        if self.output == "" or self.output == "-":
            fout = open("output/closed_eclat.txt", 'w')
            fout.write(result)
            fout.close()
            self.patternSet = utils.parser(self, result, "output/closed_eclat.txt")
            #self.patternSet = utils.parser(self, result, "-")
        return t1-t0

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

    def parser(self):
        self.patternSet = utils.parser(self, None, "output/closed_eclat.txt")
        return self.patternSet

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
