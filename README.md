Architecture Description
======================

Command:
$ python wrapper.py -c config.ini

-- The 'wrapper.py' program first uses fpMining_pure() to get closed patterns,
and uses fpMining_IDP() to get closed (or other) patterns and compares them.

-- fpMining_IDP() includes the frequent pattern mining procedure,
and then uses IDP to get closed pattern.

-- The standard output will show the time costs of eclat and (eclat plus) IDP.

-- You can manually choose which method
   (generate itemsets as a whole to IDP program or generate itemsets only with same support)
   to get closed itemsets by IDP. (line 98 and 99 in method fpMining_IDP())

**config.ini**

type: graph, sequence, itemset

support: 0.1, 0.2, ... (only float)

data: you can set the data with file name of different datasets,
      all datasets for graph, sequence, and itemset are listed in config.ini

output: you can set the output file name just as the input file name,
        but currently they are useless,
        I didn't output anything. Just parse output patterns by program

**Input:**

type: graph, itemset, sequence

constraints: frequency, cost (not implemented)

dominance: max, closed

--- Then choose specialized software.

--- And provide output file.

**Method:**
(abstract class) Mining
--> gSpan, prefixSpan, eclat

--- Parse the output file into Patterns

--- Generate IDP program and run

--- Parse the output of IDP

**Patterns:**
(abstract) Pattern
--> Graph, Sequence, Itemset
