__author__ = 'enzo'

import os, sys
import csv
import collections
from solver.Constraint import LengthConstraint, IfThenConstraint, CostConstraint
from wrapper import fpMining_pure, fpMining_postpro


def experiment(exp1=True, exp2=True, exp3=True):
    typeList = ['itemset', 'sequence', 'graph']
    supports = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.20, 0.15, 0.10]
    seq_supports = [0.4, 0.35, 0.3, 0.25, 0.20, 0.15, 0.10, 0.05, 0.025]
    fifa_seq     = [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.2]

    suppport = {("itemset",'zoo-1.txt') : supports
                ("itemset",'vote.txt'): : supports 
                ("itemset",'tic-tac-toe.txt'): supports,
                ("itemset", 'splice-1.txt'): supports, 
                ('itemset','soybean.txt'): supports, 
                ("itemset", 'primary-tumor.txt'): supports,
                ("itemset", 'mushroom.txt'): supports,
                ("itemset", 'german-credit.txt') : [0.5, 0.45, 0.4, 0.35, 0.3, 0.25, 0.20],
                #TODO do the same for seq and graphs
                }
    dominances = ['closed', 'maximal']
    it_datasets    = ['zoo-1.txt', 'vote.txt', 'tic-tac-toe.txt',
                      'splice-1.txt', 'soybean.txt', 'primary-tumor.txt',
                      'mushroom.txt'] # 'lymph.txt' is too large
    seq_datasets   = ['iprg_neg.dat', 'iprg_pos.dat', 'jmlr.dat',
                      'unix_users_neg.dat', 'unix_users_pos.dat']
    graph_datasets = ['Chemical_340', 'Compound_422', 'nctrer.gsp','yoshida.gsp', 'bloodbarr.gsp']
    datasets = {
        'itemset'  : it_datasets,
        'sequence' : seq_datasets,
        'graph'    : graph_datasets
    }
    params = dict()
    params['constraints'] = dict()
    params['constraints']['length'] = LengthConstraint(100)
    params['constraints']['ifthen'] = IfThenConstraint(-1, -1)
    params['constraints']['cost']   = CostConstraint(100, collections.defaultdict(int))

    # experiment 1
    if exp1:
        exp1_path = 'output/exp1'
        for t in typeList:
            params['type'] = t
            params['support'] = 0.2
            for d in dominances:
                results = []
                params['dominance'] = d
                for dataset in datasets[t]:
                    params['data'] = dataset
                    params['output'] = dataset.split('.')[0]+'.output'
                    _, step1_tc, step2_tc, step3_tc = fpMining_postpro(params)
                    results.append((params['data'].split('/')[-1], '{0:.4f}'.format(step1_tc),
                                    '{0:.4f}'.format(step2_tc), '{0:.4f}'.format(step3_tc))) # TODO append the number of patterns
                with open('{path}/{dominance}/{type}.csv'.format(path=exp1_path, dominance=d, type=t), 'wb') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['dataset', 'step1', 'step2', 'step3'])
                    writer.writerows(results)

    # experiment 2
    if exp2:
        exp2_path = 'output/exp2'
        for t in typeList:
            params['type'] = t
            for dataset in datasets[t]:
                results = []
                params['data'] = dataset
                params['output'] = dataset.split('.')[0]+'.output'
                params['dominance'] = 'closed'
                for s in supports:
                    params['support'] = s
                    params['data'] = dataset
                    params['output'] = dataset.split('.')[0]+'.output'
                    _, timecost_pure = fpMining_pure(params)
                    _, step1_tc, step2_tc, step3_tc = fpMining_postpro(params)
                    results.append((s, '{0:.4f}'.format(timecost_pure), '{0:.4f}'.format(step1_tc+step2_tc+step3_tc),
                                    '{0:.4f}'.format(step1_tc), '{0:.4f}'.format(step2_tc), '{0:.4f}'.format(step3_tc)))
                with open('{path}/{dominance}/{type}/{dataset}.csv'.format(path=exp2_path, dominance=params['dominance'], type=t, dataset=dataset.split('.')[0]), 'wb') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['freq', 'specialised', 'postpro', 'step1', 'step2', 'step3'])
                    writer.writerows(results)



if __name__ == '__main__':
    experiment(False, True, True)
