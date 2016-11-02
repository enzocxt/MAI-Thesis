#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Random sequence generator
    - very simple random generator of sequence of itemsets
    - a smarter generator of sequences of items based on simulated patterns
"""

import numpy as np
import sys, getopt
import warnings


"""
"""
class pattern:
    npat=0
    
    def __init__(self):
        self.sequence = []      # description of the pattern
        self.tidl=[]            # list of the transactions in which the pattern occurs
        self.pid=pattern.npat   # pattern id
        pattern.npat += 1

    """
    add an itemset at the end of the pattern
    """
    def append(self, item):
        self.sequence.append(item)
    
    
    def occurs(self, tid):
        self.tidl.append(tid)
    
    """
    length of the patterns (number of items)
    """
    def len(self):
        return len(self.sequence)
        
    def __str__(self):
        return "P"+str(self.pid)+", "+str(self.sequence) + ": " + str(self.tidl)
        
class pattern_generator:
    def __init__(self, n=100, fl="gaussian"):
        self.flaw=[]    # distribution for the item frequency: "uniform" or "gaussian"
        self.nb=n       # number of items
        if fl=="uniform":
            self.flaw=np.ones(self.nb)/self.nb
        elif fl=="gaussian":
            vec = range(0,self.nb)
            vec = [v/float(self.nb) for v in vec]
            sigma=.05
            mu=0.5
            for v in vec:
                self.flaw.append(np.exp( - (v-mu)*(v-mu)/(2*sigma*sigma)) )
            np.random.shuffle(self.flaw)
            self.flaw=self.flaw/sum(self.flaw) #normalisation
        else:
            warnings.warn("Unknown ")
        
    """
    function that generates a random item according to the item distribution modeling
    """
    def generate_item(self):
        return np.random.choice(self.nb, 1, p=self.flaw)[0]
        
    """
    - l length of the pattern
    """
    def generate_pattern(self, l=5):
        pat = pattern()
        for i in range(l):
            item = self.generate_item()
            pat.append(item)
        return pat


class sequence:
    nbs=0
    
    def __init__(self, rl =20):
        self.patterns = []
        self.seq=[]
        self.requiredlen=rl
        self.id=sequence.nbs
        sequence.nbs+=1

    """
    add a pattern without redundancy
    """
    def add_pattern(self, p):
        if not p in self.patterns:
            self.patterns.append(p)

    """
    Compute the sum of pattern length 
    """
    def __patcontentlen__(self):
        total=0
        for p in self.patterns:
            total += p.len()
        return total
    
    
    """
    Generate the sequence of items from the patterns it contains and according to the require length
    - pg : pattern generator used to generate random items to mix the pattern occurrences with random items
    """    
    def self_generate(self, pg):
        # no patterns inside: fully random sequences
        if len(self.patterns)==0:
            l=int(np.random.normal(self.requiredlen, self.requiredlen/10))
            for i in range(l):
                item = pg.generate_item()
                self.seq.append(item)
            return

        # sequence that must include patterns
        readpos = np.zeros( len(self.patterns) ) #retient la position de lecture du motif
        available=range(0, len(self.patterns))
        self.seq=[]
        lastpat=None
        while( len(available)>0 ):
            #select randomly one pattern
            if np.random.random()<float(self.requiredlen-self.__patcontentlen__())/float(self.requiredlen):
                item = pg.generate_item()
                self.seq.append(item)
                continue
            pat=available[np.random.randint(0,len(available))]
            
            #add its current item to the sequence
            pos = int(readpos[pat])
            item = self.patterns[pat].sequence[pos]
            if lastpat==pat or len(self.seq)==0 or item != self.seq[len(self.seq)-1] :
                """
                if the item is similar to the last inserted item
                (from another pattern), then it is not added (merge patterns)
                """
                self.seq.append(item)
            
            #update to pointer
            pos += 1
            readpos[pat] = pos
            #if it is the end of the patterns, it is removed from the available patterns
            if pos==self.patterns[pat].len():
                available.remove(pat)
            lastpat=pat
            
        #add random items at the end
        while np.random.random()<float(self.requiredlen-self.__patcontentlen__())/float(self.requiredlen):
            item = pg.generate_item()
            self.seq.append(item)

    """
    return an ASP string
    use predicate seq/3, where seq(S,P,I) means "sequence S at position P has the item I"
    """
    def asp(self):
        so=''
        i=0
        for s in self.seq:
            so += "seq("+str(self.id)+","+str(i)+","+str(s)+').'
            i+=1
        return so
    
    """
    string cast
    """
    def __str__(self):
        s=str(self.seq[0])
        for e in self.seq[1:]:
            s += " "+str(e)
        return s

class db_generator:

    def __init__(self):
        self.patgen = None    # last generated pattern generator
        self.patterns = []    # set of patterns
        self.db = []        # database of sequences
        
        self.nbex = 1000    # number of sequences in the database
        self.l = 30            # mean length of the sequences
        #self.fixedl = False    # fixed length (instead of a random length)
        self.n = 100        # number of items
        self.fl="uniform"    # item frequency distribution
        self.nbpat = 5        # number of the patterns
        self.lpat = 5        # mean length of the patterns
        self.th = 0.20        # pattern threshold
    
    
    """
    The function generates a set of self.nbpat patterns of mean length self.lpat.
    It uses the self.patgen pattern generator
    - Requires the self.patgen to be defined (return an empty list if not)
    """
    def generate_patterns(self):
        if self.patgen == None:
            warnings.warn("*** undefined pattern generator ***")
            return []
        patlen = [int(v) for v in np.random.normal(self.lpat,max(1,int(self.lpat/10)),self.nbpat)]
        patterns = [self.patgen.generate_pattern(l) for l in patlen]
        return patterns
    
    
    def output_patterns(self):
        s = ''
        for p in self.patterns:
            s += str(p) + "\n"
        return s
        
    """
    Generation of the sequence database
    - nb number of sequences (default)
    - th frequency threshold
    """
    def generate_sequences(self, nb=None, l=None, n=None, npat=None, lp=None, th=None):
        #update the parameters of the generation
        if not nb is None:
            self.nbex=nb
        if not l is None:
            self.l=l
        if not th is None:
            self.th=th
        if not n is None:
            self.n=n
        if not npat is None:
            self.nbpat=npat
        if not lp is None:
            self.lpat=lp
            
        #generate a set of nbex empty sequences
        self.db=[]
        for i in range(self.nbex):
            self.db.append(sequence(self.l))
    
        # create a new pattern generator        
        self.patgen = pattern_generator(n=self.n, fl=self.fl)
        
        #generate self.nbpat random patterns using the generator
        self.patterns=self.generate_patterns()
        
        #attribute transactions to the patterns
        for p in self.patterns:      
            nbocc = self.nbex*self.th  + (np.random.geometric(0.15)-1) # number of occurrences generated (randomly above the threshold)
            nbocc = min(nbocc, self.nbex)
            #generation of a random set of sequences of size nbex (ensure no repetitions)
            vec = range(0,self.nbex)    # get a set of id
            np.random.shuffle( vec )    # shuffle it a little bit
            patpos = vec[:int(nbocc)]   # take just take the require number of sequence (at the beginning)
            p.tidl = patpos
            
            for pos in patpos:
                try:
                    self.db[pos].add_pattern( p )
                except IndexError:
                    warnings.warn("*** index error: "+str(pos)+" ***")
                    pass

        #generate sequences
        for i in range(self.nbex):
            self.db[i].self_generate(self.patgen)
        return self.db


"""
Basic random sequence generation. Generate sequences of itemsets.

- seqnb: number of sequences
- length: mean length of the sequences
- itemsetSize: mean size ot the itemsets of a sequence
- maxitems: size of the vocabulary (maximum number of items)
- fixedlength: if true, all the sequences have the exact length
- asp: if true, asp predicate are outputed
- outputfile: output filename
"""
def gen_seqdb(seqnb,length,itemsetSize,maxitems,fixedlength,asp,outputfile):
    fout = open(outputfile, "w")
    for i in range(seqnb):
        if i!=0:
            fout.write("\n")
        if fixedlength:
            rlength=length
        else:
            rlength=int(np.random.normal(length,max(1,int(length/10))))
        for j in range(rlength):
            alreadyAdded=[]
            itemset=[]
            for k in range(itemsetSize):
                item = np.random.randint(0,maxitems+1,1)[0]
                while item in alreadyAdded:
                    item = np.random.randint(0,maxitems+1,1)[0]
                alreadyAdded.append(item)
                itemset.append(item)
            itemset.sort()
            for it in itemset[:-1]:
                if asp:
                    fout.write( "seq("+str(i) +","+str(j) +","+str(it) +"). ")
                else:
                    fout.write( str(it) + ":")
            if asp:
                fout.write( "seq("+str(i) +","+str(j) +","+str(itemset[len(itemset)-1]) +"). ")
            else:
                fout.write( str(itemset[len(itemset)-1]) )
            if j!=(rlength-1) and not asp:
                fout.write(",")
    fout.close()
    
    
def gen_seqdb_patterns(seqnb, length, maxitems, nbpatterns, lengthpatterns, threshold, outputfile):
    generator=db_generator()
    #generate sequences
    sequences = generator.generate_sequences(nb=seqnb, l=length, n=maxitems, npat=nbpatterns, lp=lengthpatterns, th=threshold)
    #write output
    fout = open(outputfile, "w")
    for s in sequences:
        fout.write(str(s))
        fout.write('\n')
    fout.close()
    
    filename=outputfile.rsplit(".",1)
    if len(filename)==1 or filename[1]!="lp":
        outputfile=filename[0]+".lp"
        fout = open(outputfile, "w")
        for s in sequences:
            fout.write(s.asp())
            fout.write('\n')
        fout.close()
    
    #output patterns
    filename=outputfile.rsplit(".",1)
    outputfile=filename[0]+".pat"
    fout = open(outputfile, "w")
    fout.write(generator.output_patterns())
    fout.close()


helpstring="""generation.py -n <val> -l <val> --np=<val> --lp=<val> --th=<val> --r --fl -d <val> -is <val> --asp -o <outputfile>
    * n: number of sequences (default: 100)
    * l: default length of the sequence (default: 10)
    * i: number of items per itemsets (default: 1, only with the --r option)
    * d: dictionnary size (number of different items) (default: 120)
    * r: fully random sequence (basic generator)
    * fl: fixed length (default: sequence length is a gaussian random variable, with mean length and var of length/10)
    * asp: generate ASP facts (atoms of the predicate seq/3)
    * o output filename
    * np: number of patterns (default 20, without option --r),
    * lp: mean length of patterns (default 5, without option --r),
    * th: threshold of patterns, minimum occurrence frequency in the database (default 0.1, without option --r),
    
Usage example:
    $ python generation.py -l 10 -d 20 --asp -o output.dat
    This command generates three files:
        - output.dat: a space separated file (one transaction per line)
        - output.lp: a files with atoms of seq/3 predicate
        - output.pat: description of the hidden patterns (for each hidden pattern, you have its description, a sequence of events, and its locations in the database, ie the ids of the transaction in which it is!) Note that this list may not be complete: generation of random sequences/items may create additional occurrences
"""

"""
Main function
- parse the command line arguments
- generate a database in a file
"""
def main(argv):
    seqnb=100
    length=10
    itemsetSize=1
    maxitems=120
    fixedlength=False
    asp=False
    outputfile="output.dat"
    simplegenerator=False
    nbpatterns = 20
    lengthpatterns = 5
    threshold=0.10
    
    try:
       opts, args = getopt.getopt(argv,"hn:d:l:o:i:",["nbseq=","nbitems=","length=","itemsetSize=","ofile=", "fl", "r", "asp", "np=", "lp=", "th="])
    except getopt.GetoptError:
       print helpstring
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print helpstring
           sys.exit()
       elif opt in ("-d", "--nbitems"):
           try:
               maxitems = int(arg)
           except:
               print("error with argument -d: an integer must be given")
       elif opt in ("-l", "--length"):
           try:
               length = int(arg)
           except:
               print("error with argument -l: an integer must be given")
       elif opt in ("-i", "--itemsetSize"):
           try:
               itemsetSize = int(arg)
           except:
               print("error with argument -i: an integer must be given")
       elif opt in ("-n", "--nbseq"):
           try:
               seqnb = int(arg)
           except:
               print("error with argument -n: an integer must be given")
       elif opt in ("--fl"):
           fixedlength=True
       elif opt in ("--r"):
           simplegenerator=True
       elif opt in ("--asp"):
           asp=True
       elif opt in ("-o", "--ofile"):
           outputfile = arg
       elif opt in ("--np"):
           try:
               nbpatterns = int(arg)
           except:
               print("error with argument --np: an integer must be given")
       elif opt in ("--lp"):
           try:
               lengthpatterns = int(arg)
           except:
               print("error with argument --lp: an integer must be given")
       elif opt in ("--th"):
           try:
               threshold = float(arg)
           except ValueError:
               print("error with argument --th: a float must be given")
    
    if simplegenerator:
        gen_seqdb(seqnb,length,itemsetSize,maxitems,fixedlength,asp,outputfile)
    else:
        gen_seqdb_patterns(seqnb,length,maxitems,nbpatterns, lengthpatterns, threshold, outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
