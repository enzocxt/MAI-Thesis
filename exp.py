__author__ = 'enzo'

import os, sys
import subprocess
import collections
import wrapper
from solver.Constraint import LengthConstraint, IfThenConstraint, CostConstraint
from wrapper_without_IDP import fpMining_pure, fpMining_postpro


def experiment():
    typeList = ['itemset', 'sequence', 'graph']
    supports = [0.5, 0.45, 0.4, 0.35, 0.3]
    dominances = ['closed', 'maximal']
    it_datasets    = ['zoo-1.txt', 'vote.txt', 'tic-tac-toe.txt',
                      'splice-1.txt', 'soybean.txt', 'primary-tumor.txt',
                      'mushroom.txt'] # 'lymph.txt' is too large
    seq_datasets   = ['fifa.dat', 'iprg_neg.dat', 'iprg_pos.dat', 'jmlr.dat',
                      'unix_users_neg.dat', 'unix_users_pos.dat']
    graph_datasets = ['Chemical_340', 'Compound_422', 'graph.data']
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

    fout = open('output/exp_results.txt', 'w')
    for t in typeList:
        params['type'] = t
        if t == 'graph': sys.exit(2)
        for s in supports:
            params['support'] = s
            for d in dominances:
                params['dominance'] = d
                for dataset in datasets[t]:
                    params['data'] = dataset
                    params['output'] = dataset.split('.')[0]+'.output'
                    print "\n****************************************************\n"
                    _, timecost_pure = fpMining_pure(params)
                    fout.write('Pure\t:{type},{support},{dominance},{dataset}:{timecost:.4f}\n'.format(
                        type=params['type'], support=params['support'], dominance=params['dominance'],
                        dataset=params['data'].split('/')[-1], timecost=timecost_pure
                    ))
                    _, step1_tc, step2_tc, step3_tc = fpMining_postpro(params)
                    timecost_postpro = step1_tc + step2_tc + step3_tc
                    fout.write('Postpro\t:{type},{support},{dominance},{dataset}:{timecost:.4f},{step1:.4f},{step2:.4f},{step3:.4f}\n'.format(
                        type=params['type'], support=params['support'], dominance=params['dominance'], dataset=params['data'].split('/')[-1],
                        timecost=timecost_postpro, step1=step1_tc, step2=step2_tc, step3=step3_tc
                    ))
                    print "\n****************************************************\n"
    fout.close()




if __name__ == '__main__':
    experiment()