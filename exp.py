__author__ = 'enzo'

import os
import subprocess
import wrapper


def test_perf(config_file):
    #config_file = 'config.ini'
    # input_path = os.getcwd() + '/data/eclat/'
    # output_path = os.getcwd() + '/output/eclat/'
    input_path = './data/eclat/'
    output_path = './output/eclat/'
    input_files = os.listdir(input_path)
    perfFin = open('./output/performance_max.txt', 'a')

    files = ['hepatitis.txt', 'lymph.txt', 'primary-tumor.txt', 'soybean.txt', 'zoo-1.txt']
    files = ['zoo-1.txt']
    for input_file in files:
        child = subprocess.Popen(['python', 'wrapper.py',
                                  '-c', config_file,
                                  '-i', input_path + input_file,
                                  '-o', output_path + input_file],
                                 stdout=subprocess.PIPE)
        stdOutput = child.stdout.read()
        perfFin.write(stdOutput)

    perfFin.close()



if __name__ == '__main__':
    configs = ['config_max_25.ini', 'config_max_20.ini']
    for f in configs:
        test_perf(f)
