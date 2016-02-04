# inst_eval.py

An implementation of the INST information retrieval evaluation measure in the style of trec_eval.

### About INST

INST is an evaluation measure outlined in:

A. Moffat, P. Bailey, F. Scholer, P. Thomas. *[INST: An Adaptive Metric for Information Retrieval Evaluation](http://dl.acm.org/citation.cfm?id=2838938)*. ADCS'15 Proceedings of the 20th Australasian Document Computing Symposium. Sydney, Australia, December 2015.

### Setting up inst_eval.y

inst_eval.py is run as a standalone program. It requires Python 2.7 to be installed.

### Using inst_eval.py

For usage information run:

`./inst_eval.py -h`

This will print the following:

	usage: inst_eval.py [-h] -n EVAL_DEPTH [-T OVER_WRITE_T]
	                    trec_qrel_file trec_results_file T_per_query
	
	Implementation of the INST evaluation measure from 'INST: An Adaptive Metric
	for Information Retrieval Evaluation', ACDS2015.
	
	positional arguments:
	  trec_qrel_file        TREC style qrel file.
	  trec_results_file     TREC style results file.
	  T_per_query           Tab separated file indicating value of T for each
	                        query: QueryId T
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -n EVAL_DEPTH, --eval_depth EVAL_DEPTH
	                        Max depth to evaluate at.
	  -T OVER_WRITE_T, --over_write_T OVER_WRITE_T
	                        Set all T values to supplied constant.

