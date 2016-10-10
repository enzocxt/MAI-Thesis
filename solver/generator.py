__author__ = 'enzo'

debugging  = True # delete later


import os, sys
import platform
import subprocess
from string import Template
from Pattern import *
import time


class IDPGenerator:
    def __init__(self, inputs):
        self.idp_path = os.getcwd() + '/IDP/'
        self.type = inputs['type']
        if 'dominance' in inputs:
            self.dominance = inputs['dominance']
        else:
            self.dominance = ''


    def gen_IDP_sequence_constraints(self, constraints, sequences, filename):
        global debugging
        if debugging:
            t_start = time.time()
        file_path = os.getcwd() + '/IDP/%s.idp' % filename
        class_file = open(file_path, 'w')
        lines = []
        template_file = open(os.getcwd() + '/IDP/posprocessing_sequence.template', 'r')
        tmpl = Template(template_file.read())

        idp_sequences = ''
        for seq_i, sequence in enumerate(sequences):
            index, items, support = str(sequence).split(':')
            items = items.split()
            idp_items = ''
            for i, it in enumerate(items):
                idp_items += '({0},{1},{2});'.format(index, i, it)
            idp_sequences += idp_items + '\n'
        idp_sequences = idp_sequences[:-1]

        final_theory = '\t{\n\toutput(patternID) <- '
        if 'length' in constraints and 'cost' in constraints and 'ifthen' in constraints:
            final_theory += 'len_constraint(patternID) & cost_constraint(patternID) & if_then_constraint(patternID).'
        elif 'length' in constraints and 'cost' in constraints:
            final_theory += 'len_constraint(patternID) & cost_constraint(patternID).'
        elif 'length' in constraints and 'ifthen' in constraints:
            final_theory += 'len_constraint(patternID) & if_then_constraint(patternID).'
        elif 'cost' in constraints and 'ifthen' in constraints:
            final_theory += 'cost_constraint(patternID) & if_then_constraint(patternID).'
        elif 'length' in constraints:
            final_theory += 'len_constraint(patternID).'
        elif 'cost' in constraints:
            final_theory += 'cost_constraint(patternID).'
        elif 'ifthen' in constraints:
            final_theory += 'if_then_constraint(patternID).'
        else:
            pass
        final_theory += '\n\t}\n'

        vocabulary, theory, structure = '', '', ''
        if 'length' in constraints:
            vocabulary += constraints['length'].generate_vocabulary() + '\n'
            theory += constraints['length'].generate_theory() + '\n'
            structure += constraints['length'].generate_structure() + '\n'
        if 'cost' in constraints:
            vocabulary += constraints['cost'].generate_vocabulary() + '\n'
            theory += constraints['cost'].generate_theory() + '\n'
            structure += constraints['cost'].generate_structure() + '\n'
        if 'ifthen' in constraints:
            vocabulary += constraints['ifthen'].generate_vocabulary() + '\n'
            theory += constraints['ifthen'].generate_theory() + '\n'
            structure += constraints['ifthen'].generate_structure() + '\n'

        lines.append(tmpl.substitute(
            VOCABULARY=vocabulary,
            THEORY=theory,
            FINAL_THEORY=final_theory,
            SEQUENCES=idp_sequences,
            STRUCTURE=structure
        ))

        class_file.writelines(lines)
        class_file.close()
        if debugging:
            t_end = time.time()
            print("GENERATION TIME FOR IDP", t_end-t_start)


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
        structures = ''
        models = ''

        for itemset, its_to_check in mapping.items():
            idp_itemsets = ''
            for itemset_i, itemset in enumerate(its_to_check):
                index, items, support = str(itemset).split(':')
                if itemset_i % 5 == 0:
                    idp_itemsets += '\n'
                items = items.split()
                idp_items = ''
                for i in items:
                    idp_items += '({0},{1};'.format(index, i)
                idp_itemsets += idp_items
            idp_itemsets = idp_itemsets[:-1]

            structure = 'Structure S_%s:V{\n\tselected_itemset = {%s}\n\titemset = {%s}}\n\n' % (str(itemset.id), str(itemset.id), idp_itemsets)
            structures += structure
            printmodel = '\nprintmodels(modelexpand(T,S_{0}))\n'.format(itemset.id)
            models += printmodel

        file_path = os.getcwd() + '/IDP/%s.idp' % filename
        class_file = open(file_path, 'w')
        lines = []
        template_file = open(os.getcwd() + '/IDP/{0}_itemset_group.template'.format(self.dominance), 'r')
        tmpl = Template(template_file.read())

        # template substitute
        lines.append(tmpl.substitute(STRUCTURES=structures, PRINTMODELS=models))
        # write code to file
        class_file.writelines(lines)
        class_file.close()


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
        print 'Generating itemset idp code...'
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

    def gen_IDP_sequence(self, sequences, filename, selected_index):
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
        self.generate(idp_sequences, supports, filename, selected_index)

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
        template_file.close()

        # print('\nGenerate idp file %s over. ~ ~\n' % file_path)


    def run_IDP(self, filename):
        global debugging
        if debugging:
            t_start = time.time()
            
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
        with open("tmp/fnull","w") as FNULL:
          child = subprocess.Popen([idpBin, idpProgram], stdout=subprocess.PIPE,stderr=FNULL)
        stdOutput = child.stdout.read()
       #print stdOutput
        '''
        with open(idp_tmp_output,"r") as idp_tmp_file:
          stdOutput = idp_tmp_file.read()
        '''

        if debugging:
            t_end = time.time()
            print("TIME TO RUN IDP PROGRAM",t_end-t_start)
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
