import os, sys, time
import platform
import subprocess
import utils
from fqPattern import Itemset

# gSpan command:
# ./gSpan -file [file_name] -support [support: float] &> log

# eclat command:
# ./eclat [options] infile [outfile]

class Mining(object):
    """Abstract class"""

    def __init__(self, inputs):
        # inputs{'type': 'itemset', 'matching': 'exact', 'constraints': 'frequency', 'dominance': 'max'}
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

class eclat(Mining):
    """Use eclat to mining frequent itemsets"""

    def __init__(self, inputs):
        Mining.__init__(self, inputs)

    def mining(self):
        """Mining frequent itemsets by (closed) eclat"""
        if platform.system() == "Linux":
          eclat = "./exec/eclat"
        else:
          eclat = "eclat"
        options = ''
        if self.support:
            options += '-s%s' % self.support
        if self.dominance == 'max':
            options += 'tm'
        elif self.dominance == 'closed':
            options += 'tc'

        t0 = time.time()
        #child = subprocess.Popen([eclat, options, self.datafile, self.output], stdout=subprocess.PIPE)
        child = subprocess.Popen([eclat, options, self.datafile, "-"], stdout=subprocess.PIPE)
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

        t0 = time.time()
        child = subprocess.Popen([eclat, "-s%s" % self.support, self.datafile, ""], stdout=subprocess.PIPE)
        t1 = time.time()
        result = child.stdout.read()
        #print "time cost of eclat : %s" % (t1-t0)
        if self.dominance == 'max':
            self.maxParser(result)
        elif self.dominance == 'closed':
            #closedPatterns, t1 = self.closedParser_old(result)
            closedPatterns, t1 = self.closedParser_New(result)
            return closedPatterns, t1-t0

    def parser(self):
        self.patternSet = utils.parser(self, None, "output/closed_eclat.txt")
        return self.patternSet

    def maxParser(self, stdOutput):
        """For maximal item sets"""
        pass

    def closedParser_old(self, stdOutput):
        """For closed item sets"""
        # itemsets: a dictionary of itemset list
        # itemsets of the same list have same support
        itemsets = {}
        stdOutput = stdOutput.split('\n')
        # pass the description lines
        tmp = stdOutput.pop()
        tmpList = tmp.split(' ')
        while not tmpList[0].isdigit():
            tmp = stdOutput.pop()
            tmpList = tmp.split(' ')
        stdOutput.append(tmp)

        for line in stdOutput:
            line.strip('\n')
            items = line.split(' ')
            support = items.pop()
            support = float(support[1:-1])
            itemset = Itemset(items, support)

            # if itemsets dictionary has support of this itemset
            # add this itemset to that list
            # else add this itemset as a new itemset list

            # old way: add itemset to list in the ascending order of size
            # if itemsets.has_key(itemset.support):
                #i = 0
                #while i < len(itemsets[itemset.support]):
                    #if itemsets[itemset.support][i].size >= itemset.size:
                    #    itemsets[itemset.support].insert(i, itemset)
                    #    break
                #    i += 1
                #if i == len(itemsets[itemset.support]):
                #    itemsets[itemset.support].append(itemset)

            # new way to insert itemset, regarless of order
            if itemsets.has_key(itemset.support):
                itemsets[itemset.support].append(itemset)
            else:
                itemsets[itemset.support] = [itemset]

        # find closed itemset
        closedItemset = []
        # old way: itemsets stored in order
        # for list in itemsets.values():
        #    for i in range(len(list)-1):
        #        if utils.checkClosed(list[i], list[i+1:]):
        #            closedItemset.append(list[i])
        #    closedItemset.append(list[-1])

        # new way: itemsets stored by appending
        for list in itemsets.values():
            for i in range(len(list)):
                if utils.checkClosed(list[i], list):
                    closedItemset.append(list[i])
        t1 = time.time()

        # not necessary, just write the result to file for check
        fout = open('output/python_process.txt', 'w')
        for itemset in closedItemset:
            fout.write("%s%s\n" % (itemset.itemset, itemset.support))
        fout.close()

        return closedItemset, t1


    def closedParser_New(self, stdOutput):
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

        #closedParserTime1 = time.time()
        #print "closedParserTime : %s" % (closedParserTime1 - closedParserTime0)

        def checkClosed(itemset, itemsetList):
            for it in itemsetList:
                if len(itemset) >= len(it):
                    continue
                elif itemset < it:
                    return False
            return True

        # find closed itemset
        #checkClosedTime0 = time.time()
        closedItemset = []
        for list in itemsets.values():
            for i in range(len(list)):
                if checkClosed(list[i], list):
                    closedItemset.append(list[i])
        t1 = time.time()
        #checkClosedTime1 = time.time()
        #print "checkClosedTime : %s" % (checkClosedTime1 - checkClosedTime0)

        return closedItemset, t1
