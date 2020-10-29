# inst_eval.py

An implementation of the INST information retrieval evaluation measure in the style of trec_eval.

### About INST

INST is an evaluation measure outlined in:

A. Moffat, P. Bailey, F. Scholer, P. Thomas. *[INST: An Adaptive Metric for Information Retrieval Evaluation](http://dl.acm.org/citation.cfm?id=2838938)*. ADCS'15 Proceedings of the 20th Australasian Document Computing Symposium. Sydney, Australia, December 2015.

We thank Moffat and Bailey for providing an initial implementation of INST from which this code was developed.

If you do use our inst_eval implementation then please include citiations to both the Moffat et al. paper and to our paper:

B. Koopman and G. Zuccon. *[A test collection for matching patient trials](https://dl.acm.org/doi/abs/10.1145/2911451.2914672?casa_token=5NSRpXeP31IAAAAA:q6gcCDnYXDm2GVf0MuDTqvZiVZqsk2h8Rnq8tEV-6-fZqXkpWILZFCIvugXKrdRM2-E-ToKg4Vtz6w)*. In Proceedings of the 39th annual international ACM SIGIR conference on research and development in information retrieval, Pisa, July 2016.

### Setting up inst_eval.py

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
	                        query: QueryId<tab>T
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -n EVAL_DEPTH, --eval_depth EVAL_DEPTH
	                        Max depth to evaluate at.
	  -T OVER_WRITE_T, --over_write_T OVER_WRITE_T
	                        Set all T values to supplied constant.

