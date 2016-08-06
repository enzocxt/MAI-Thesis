__author__ = 'enzo'


import os
import platform
import subprocess
from string import Template


class IDPGenerator:
    def __init__(self, inputs):
        self.idp_path = os.getcwd() + '/IDP/'
        if 'dominance' in inputs:
            self.dominance = inputs['dominance']
        else:
            self.dominance = ''

    def generate(self, itemsets, supports, filename):
        file_path = os.getcwd() + '/IDP/%s.idp' % filename
        class_file = open(file_path, 'w')
        lines = []

        # template file
        template_file = open(os.getcwd() + '/IDP/{0}_itemset.template'.format(self.dominance), 'r')
        tmpl = Template(template_file.read())

        # template substitute
        lines.append(tmpl.substitute(
                    ITEMSET=itemsets,
                    SUPPORT=supports
                    ))

        # write code to file
        class_file.writelines(lines)
        class_file.close()

        # print('\nGenerate idp file %s over. ~ ~\n' % file_path)


    def gen_IDP_code(self, patterns, filename):
        itemsets, supports = '', ''

        for itemset in patterns:
            index, items, support = str(itemset).split(':')
            supports += '({0},{1});'.format(index, support)
            items = items.split()
            idp_items = ''
            for i in items:
                idp_items += '({0},{1});'.format(index, i)
            itemsets += idp_items

        # eleminate the last ';' in supports
        supports = supports[:-1]
        itemsets = itemsets[:-1]
        self.generate(itemsets, supports, filename)


    def run_IDP(self, filename):
        '''run IDP program to get closed patterns from frequent patterns'''
        if platform.system() == 'Linux':
            idpBin = '/Users/enzo/Projects/Thesis/idp-Linux/bin/idp'
        else:
            idpBin = '/Users/enzo/Projects/Thesis/idp-3.5.0-Mac-OSX/bin/idp'
        idpProgram = '{0}{1}.idp'.format(self.idp_path, filename)
        child = subprocess.Popen([idpBin, idpProgram], stdout=subprocess.PIPE)
        stdOutput = child.stdout.read()
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
