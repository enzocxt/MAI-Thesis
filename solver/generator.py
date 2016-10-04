__author__ = 'enzo'


import os, sys
import platform
import subprocess
from string import Template
from Pattern import *


class IDPGenerator:
    def __init__(self, inputs):
        self.idp_path = os.getcwd() + '/IDP/'
        self.type = inputs['type']
        if 'dominance' in inputs:
            self.dominance = inputs['dominance']
        else:
            self.dominance = ''

    def gen_IDP_code_group(self, mapping, filename):
        if len(mapping.values()) == 0:
            print 'No need generate IDP program!'
            return
        if isinstance(mapping.keys()[0], Itemset):
            self.gen_IDP_itemset_group(mapping, filename)
        elif isinstance(mapping.keys()[0], Sequence):
            self.gen_IDP_sequence_group(mapping, filename)
        elif isinstance(mapping.keys()[0], Graph):
            self.gen_IDP_sequence_group(mapping, filename)
        else:
            print 'Do not support this type!'
            sys.exit(2)

    def gen_IDP_itemset_group(self, mapping, filename):
        pass

    def gen_IDP_sequence_group(self, mapping, filename):
        structures = ''
        models = ''

        for seq, seqs_to_check in mapping.items():
            idp_sequences = ''
            for seq_i, sequence in enumerate(seqs_to_check):
                index, items, support = str(sequence).split(':')
                if seq_i % 5 == 0:
                    idp_sequences += '\n'
                items = items.split()
                idp_items = ''
                for i, it in enumerate(items):
                    idp_items += '({0},{1},{2});'.format(index, i, it)
                    if i % 5 == 0:
                        idp_items += '\n'
                idp_sequences += idp_items
            idp_sequences = idp_sequences[:-1]

            structure = 'Structure S_%s:V{\n\tselected_seq = {%s}\n\tseq = {%s}}\n\n' % (str(seq.id), str(seq.id), idp_sequences)
            structures += structure
            printmodel = '\nprintmodels(modelexpand(T,S_{0}))\n'.format(seq.id)
            models += printmodel

        file_path = os.getcwd() + '/IDP/%s.idp' % filename
        class_file = open(file_path, 'w')
        lines = []
        template_file = open(os.getcwd() + '/IDP/{0}_sequence_group.template'.format(self.dominance), 'r')
        tmpl = Template(template_file.read())

        # template substitute
        lines.append(tmpl.substitute(STRUCTURES=structures, PRINTMODELS=models))
        # write code to file
        class_file.writelines(lines)
        class_file.close()


    def gen_IDP_graph_group(self, mapping, filename):
        pass

    def gen_IDP_code(self, patterns, filename, index=None):
        if len(patterns) == 0:
            print 'No result patterns!'
            sys.exit(2)
        if isinstance(patterns[0], Itemset):
            if index:
                self.gen_IDP_itemset_iterative(patterns, filename, index)
            else:
                self.gen_IDP_itemset(patterns, filename)
        elif isinstance(patterns[0], Sequence):
            self.gen_IDP_sequence(patterns, filename, index)
        elif isinstance(patterns[0], Graph):
            self.gen_IDP_graph(patterns, filename)
        else:
            print 'Do not support this type!'
            sys.exit(2)

    def gen_IDP_itemset(self, itemsets, filename):
        print 'generating itemset idp code...'
        idp_itemsets, supports = '', ''

        for itemset in itemsets:
            index, items, support = str(itemset).split(':')
            supports += '({0},{1});'.format(index, support)
            items = items.split()
            idp_items = ''
            for i in items:
                idp_items += '({0},{1});'.format(index, i)
            idp_itemsets += idp_items

        # eleminate the last ';' in supports
        supports = supports[:-1]
        idp_itemsets = idp_itemsets[:-1]
        self.generate(idp_itemsets, supports, filename)

    def gen_IDP_itemset_iterative(self, itemsets, filename, index):
        idp_itemsets, supports = '', ''
        patternIndex = index

        for itemset in itemsets:
            index, items, support = str(itemset).split(':')
            supports += '({0},{1});'.format(index, support)
            items = items.split()
            idp_items = ''
            for i in items:
                idp_items += '({0},{1});'.format(index, i)
            idp_itemsets += idp_items

        # eleminate the last ';' in supports
        supports = supports[:-1]
        idp_itemsets = idp_itemsets[:-1]
        self.generate(idp_itemsets, supports, filename, patternIndex)

    def gen_IDP_sequence(self, sequences, filename, index):
        idp_sequences, supports = '', ''

        for seq_i, sequence in enumerate(sequences):
            index, items, support = str(sequence).split(':')
            supports += '({0},{1});'.format(index, support)
            if seq_i % 5 == 0:
              supports += "\n"
              idp_sequences += "\n"
            items = items.split()
            idp_items = ''
            for i, it in enumerate(items):
                idp_items += '({0},{1},{2});'.format(index, i, it)
                if i % 5 == 0:
                  idp_items += "\n"
            idp_sequences += idp_items

        # eleminate the last ';' in supports
        supports = supports[:-1]
        idp_sequences = idp_sequences[:-1]
        self.generate(idp_sequences, supports, filename, index)

    def gen_IDP_graph(self, graphs, filename):
        pass

    def generate(self, patterns, supports, filename, index=None):
        file_path = os.getcwd() + '/IDP/%s.idp' % filename
        class_file = open(file_path, 'w')
        lines = []

        if self.type == 'itemset':
            # template file
            template_file = open(os.getcwd() + '/IDP/{0}_itemset.template'.format(self.dominance), 'r')
            tmpl = Template(template_file.read())

            # template substitute
            if not index:
                lines.append(tmpl.substitute(
                        ITEMSET=patterns,
                        SUPPORT=supports
                        ))
            else:
                lines.append(tmpl.substitute(
                        INDEX=index,
                        ITEMSET=patterns,
                        SUPPORT=supports
                        ))
        elif self.type == 'sequence':
            template_file = open(os.getcwd() + '/IDP/{0}_sequence.template'.format(self.dominance), 'r')
            tmpl = Template(template_file.read())

            # template substitute
            lines.append(tmpl.substitute(
                        INDEX=index,
                        SEQUENCE=patterns,
                        SUPPORT=supports
                        ))
        elif self.type == 'graph':
            template_file = open(os.getcwd() + '/IDP/{0}_graph.template'.format(self.dominance), 'r')
            tmpl = Template(template_file.read())

            # template substitute
            lines.append(tmpl.substitute(
                        GRAPH=patterns,
                        SUPPORT=supports
                        ))

        # write code to file
        class_file.writelines(lines)
        class_file.close()

        # print('\nGenerate idp file %s over. ~ ~\n' % file_path)


    def run_IDP(self, filename):
        '''run IDP program to get closed patterns from frequent patterns'''
        if platform.system() == 'Linux':
            idpBin = 'idp' # don't hardcode the absolute paths, it never ends well, let's say IDP must be installed and found in PATH variable?
        else:
            idpBin = '/Users/enzo/Projects/Thesis/idp-3.5.0-Mac-OSX/bin/idp'
        idpProgram = '{0}{1}.idp'.format(self.idp_path, filename)
        idp_tmp_output = "tmp/idp_out"

        '''
        command = "{idp} {program}".format(idp=idpBin, program=idpProgram)
        os.system(command)
        print "\n************\nIn process %s" % os.getpid()

        command = "{idp} {program} > {idp_tmp_output}".format(idp=idpBin, program=idpProgram,idp_tmp_output=idp_tmp_output)
    #   print "executing IDP command: " +  command
        os.system(command)
        '''
        child = subprocess.Popen([idpBin, idpProgram], stdout=subprocess.PIPE)
        stdOutput = child.stdout.read()
        #print stdOutput
        '''
        with open(idp_tmp_output,"r") as idp_tmp_file:
          stdOutput = idp_tmp_file.read()
        '''

        return stdOutput


    def parser_from_file(self, filename):
        itemsets = None
        with open(self.idp_path + '{0}.dat'.format(filename), 'r') as idp_fin:
            for line in idp_fin:
                if 'output' in line:
                    line = line.strip()
                    line = line.replace(' ', '')
                    line = line.strip('\t')
                    i = 0
                    while line[i] != '{':
                        i += 1
                    itemsets = line[i+1:-1].split(';')
                    break
        # return indices of closed frequent itemsets
        return [int(i) for i in itemsets]


    def parser_from_stdout(self, stdOutput):
        itemsets = None
        stdOutput = stdOutput.split('\n')
        for line in stdOutput:
            if 'output' in line:
                line = line.strip()
                line = line.replace(' ', '')
                line = line.strip('\t')
                i = 0
                while line[i] != '{':
                    i += 1
                itemsets = line[i+1:-1].split(';')
                break
        # return indices of closed frequent itemsets
        return [int(i) for i in itemsets]
