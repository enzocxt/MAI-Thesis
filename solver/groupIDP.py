__author__ = 'enzo'

from multiprocessing import Process, Pool, Lock
import os, time, random


def groupIDP(mapping, idp_gen, idp_program_name):
    idp_gen.gen_IDP_code_group(mapping, idp_program_name)
    lock.acquire()
    output = idp_gen.run_IDP(idp_program_name)
    print output
    print "************************"
    lock.release()

    nonclosed_indices = set()
    lines = output.split('\n')
    for line in lines:
        if 'selected_seq' in line:
            nonclosed_indices.add(int(line[19]))
    return nonclosed_indices


def init(l):
    global lock
    lock = l


def async_mapping(mapping_groups, idp_gen, idp_program_base):
    lock = Lock()
    pool = Pool(initializer=init, initargs=(lock,))
    results = []
    output = set()

    for i, mapping in enumerate(mapping_groups):
        results.append(pool.apply_async(groupIDP, args=(mapping, idp_gen, '{0}_{1}'.format(idp_program_base, str(i)))))
    pool.close()
    pool.join()

    for res in results:
        output |= res.get()

    return output


# without lock
def groupIDP_withoutLock(mapping, idp_gen, idp_program_name):
    idp_gen.gen_IDP_code_group(mapping, idp_program_name)
    output = idp_gen.run_IDP(idp_program_name)
    print output
    print "************************"

    nonclosed_indices = set()
    lines = output.split('\n')
    for line in lines:
        if 'selected_seq' in line:
            nonclosed_indices.add(int(line[19]))
    return nonclosed_indices


def async_mapping_withoutLock(mapping_groups, idp_gen, idp_program_base):
    pool = Pool()
    results = []
    output = set()

    for i, mapping in enumerate(mapping_groups):
        results.append(pool.apply_async(groupIDP_withoutLock, args=(mapping, idp_gen, '{0}_{1}'.format(idp_program_base, str(i)))))
    pool.close()
    pool.join()

    for res in results:
        output |= res.get()

    return output



# For test
def long_time_task(name):
    print 'Run task %s (%s)...' % (name, os.getpid())
    start = time.time()
    time.sleep(random.random() * 3)
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))

if __name__=='__main__':
    print 'Parent process %s.' % os.getpid()
    p = Pool()
    for i in range(5):
        p.apply_async(long_time_task, args=(i,))
    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'

'''
class idpProcess(Process):
    def __init__(self):
        Process.__init__(self)

    def run(self):
        pass

class sequenceIDPProcess(Process):
    def __init__(self, mapping, idp_gen, idp_program_name):
        Process.__init__(self)
        self.mapping = mapping
        self.idp_gen = idp_gen
        self.idp_program_name = idp_program_name

    def run(self):
        self.idp_gen.gen_IDP_code_group(self.mapping, self.idp_program_name)
        output = self.idp_gen.run_IDP(self.idp_program_name)
        print output
'''