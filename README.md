Architecture Description
======================

**Input:**
type: graph, itemset, sequence
matching: exact, delta-gap
constraints: frequency, cost
dominance: max, min, closed

--- Then choose specialized software.
--- And provide output file.

**Method:**
(abstract class) Mining
--> gSpan, eclat

--- Parse the output file into Patterns
--- Call utils.parser()
--->Call specific parser method for Graphs/Itemsets/Sequences

**Patterns:**
(abstract) Pattern
--> Graph, Itemset, Sequence

Current functions
=======================
The only kind of command that this program could execute:
$	python wrapper.py -T itemset -i [./eclatData/...] -o [./output/...]

The other parameters and options will be implemented later.
