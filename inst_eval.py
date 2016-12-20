#!/usr/bin/env python
'''
Python implementation of the INST evaluation measure, as described in:

http://dl.acm.org/citation.cfm?id=2838938
@inproceedings{moffat2015inst,
    title={INST: An Adaptive Metric for Information Retrieval Evaluation},
    author={Moffat, Alistair and Bailey, Peter and Scholer, Falk and Thomas, Paul},
    booktitle={Proceedings of the 20th Australasian Document Computing Symposium (ADCS'15)$\}$},
    year={2015},
    organization={ACM--Association for Computing Machinery$\}$}
}

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
'''

import argparse
from math import pow
import logging

def read_trec_results(trec_results_file):
    '''
    Read a TREC style results file and return a dict:
        QueryId -> [ (docName, rankPos, score, runId) ]
    '''
    trec_results = {}
    with open(trec_results_file) as fh:
        for line in fh:
            try:
                query, Q0, doc, rank, scoreStr, runid = line.strip().split()
                trec_results[query] = trec_results.get(query, []) + [(doc, rank, float(scoreStr), runid)]
            except Exception as e:
                print "Error: unable to split line in 6 parts", line
                raise e
    return trec_results

def read_trec_qrels(trec_qrel_file):
    '''
    Read a TREC style qrel file and return a dict:
        QueryId -> docName -> relevance
    '''
    qrels = {}
    with open(trec_qrel_file) as fh:
        for line in fh:
            try:
                query, zero, doc, relevance = line.strip().split()
                docs = qrels.get(query, {})
                docs[doc] = float(relevance)
                qrels[query] = docs
            except Exception as e:
                print "Error: unable to split line in 4 parts", line
                raise e
    return qrels

def read_T_per_query(T_per_query_file):
    '''
    Read a Tab separated file indicating value of T for each query and return a dict:
        QueryId -> T
    '''
    Ts = {}
    with open(T_per_query_file) as fh:
        for line in fh:
            try:
                query, T = line.strip().split()
                Ts[query] = int(T)
            except Exception as e:
                print "Error: unable to split line in 2 parts", line
                raise e
    return Ts

def find_max_graded_label(qrels):
    '''
    Determine from the qrels what the maximum graded relevance label is.
    This will be used later bound turned graded labels to [0..1].
    '''
    return max([rel for doc in qrels.values() for rel in doc.values()])

def inst_algorithm(T, ranked_gains, n, defaultValue):
    '''
    Implementation of Algorithm 1 from Moffat et al, 2015.
    '''
    score = 0.0
    N = int(2*pow(10,4) if T<=5 else 2*pow(10,5))
    maxN = max(n,N)
    W = [0]*(maxN+2) # the +2 is just to avoid having to check we don't compute the last W.[i+1]
    C = [0]*(maxN+1) # the +1 is to allow us to use the rank positions from 1 .. N, rather than using a 0-base
    sumW = 0.0
    T_is = [0]*(maxN+1)
    T_is[0] = T
    W[1] = 1.0

    for i in range(1, maxN):
        r_i = 0.0

        if i > n:
            r_i = defaultValue
        elif i > len(ranked_gains):
            r_i = defaultValue
        elif ranked_gains[i-1] == -1: # use -1.0 to indicate undefined values for items in the ranking
            r_i = defaultValue
        else:
            r_i = ranked_gains[i-1]

        T_is[i] = T_is[i-1] - r_i
        score = score + r_i * W[i]
        sumW = sumW + W[i]

        C[i] = pow((float(i) + T + T_is[i] - 1) / (float(i) + T + T_is[i]), 2)
        W[i+1] = W[i] * C[i]

    return score / sumW


def calc_ranked_gains(ranked_list, qrels, max_graded_label):
    '''
    Using qrels, turns a ranked list into array of gains.
    Note: unjudged documents are marked with gain of -1.0.
    '''
    ranked_gains = []
    for (doc, rank, score, runid) in ranked_list:
        if doc in qrels:
            ranked_gains.append(qrels[doc] / float(max_graded_label))
        else:
            ranked_gains.append(-1.0)
    return ranked_gains

def print_stats(num_ret, num_rel, num_rel_ret, score_min, score_max, residual, qId='all', num_q=0):
    '''
    Print results in the same format as trec_eval.
    '''
    if num_q > 0:
        print "num_q\t\t%s\t%d" % (qId, num_q )    
    print "num_ret\t\t%s\t%d" % (qId, num_ret )
    print "num_rel\t\t%s\t%d" % (qId, num_rel )
    print "num_rel_ret\t%s\t%d" % (qId, num_rel_ret)
    print "inst_min\t%s\t%.4f" % (qId, score_min)
    print "inst_max\t%s\t%.4f" % (qId, score_max)
    print "inst_res\t%s\t%.4f" % (qId, residual)

def inst_eval(results, qrels, Ts, max_graded_label, complete_qrel_queries):
    '''
    Main method that calls inst_algorithm for each query.
    Accumulates and prints overall summary statistics.
    '''
    totals = {}

    query_list = sorted(qrels) if complete_qrel_queries else sorted(results)

    query_count = 0
    for qId in query_list:
        try:
            T = Ts[qId]
        except KeyError as ke:
            logging.error("No T was found for query %s." % qId) # logs to stderr
            continue # skip this query and continue

        if qId not in qrels: # can't do anything if there are no qrels - skip this query
            logging.error("No qrels were found for query %s." %  qId) # logs to stderr
            continue

        if qId in results or complete_qrel_queries: 

            if qId not in results:
                logging.warn("No results found for query %s", qId)
                results[qId] = []

            ranked_gains = calc_ranked_gains(results[qId], qrels[qId], max_graded_label)

            # get the scores - assume score is 0.0000 if there are no results
            score_min = inst_algorithm(T, ranked_gains, len(qrels[qId]), 0.0) if len(ranked_gains) > 0 else 0.000 # assume unjudged are all not relevant
            score_max = inst_algorithm(T, ranked_gains, len(qrels[qId]), 1.0) if len(ranked_gains) > 0 else 0.000 # assume unjudged are all relevant
            

            residual = score_max - score_min

            num_ret = len(results[qId])
            num_rel = len([rel for rel in qrels[qId].values() if rel > 0.0])
            num_rel_ret = len([g for g in ranked_gains if g > 0.0])

            print_stats(num_ret, num_rel, num_rel_ret, score_min, score_max, residual, qId)

            totals['num_ret'] = totals.get('num_ret', 0.0) + num_ret
            totals['num_rel'] = totals.get('num_rel', 0.0) + num_rel
            totals['num_rel_ret'] = totals.get('num_rel_ret', 0.0) + num_rel_ret
            totals['score_min'] = totals.get('score_min', 0.0) + score_min
            totals['score_max'] = totals.get('score_max', 0.0) + score_max
            totals['residual'] = totals.get('residual', 0.0) + residual

            query_count = query_count + 1

        else: # there are no retrieval results for this query:
            logging.error("No results were found for query %s." %  qId) # logs to stderr
            continue # skip this query and continue

    if len(totals) > 0:    
        totals = dict([(stat, float(value)/query_count) for (stat, value) in totals.items()])
        totals['num_q'] = len(results)
        print_stats(**totals)

        

if __name__ == "__main__":
    '''
    Main method: collection command line args and call inst_eval.
    '''
    arg_parser = argparse.ArgumentParser(description="Implementation of the INST evaluation measure from 'INST: An Adaptive Metric for Information Retrieval Evaluation', ACDS2015.")
    arg_parser.add_argument("trec_qrel_file", help="TREC style qrel file.")
    arg_parser.add_argument("trec_results_file", help="TREC style results file.")
    arg_parser.add_argument("T_per_query", help="Tab separated file indicating value of T for each query: QueryId<tab>T")
    arg_parser.add_argument("-T", "--over_write_T", help="Set all T values to supplied constant.", type=int, required=False)
    arg_parser.add_argument("-c", "--complete_qrel_queries", help="Same as -c in trec_eval: Average over the complete set of queries in the relevance judgements instead of the queries in the intersection of relevance judgements and results.  Missing queries will contribute a value of 0 to all evaluation measures", action="store_true", default=False)

    args = arg_parser.parse_args()
    qrels = read_trec_qrels(args.trec_qrel_file)
    results = read_trec_results(args.trec_results_file)
    Ts = read_T_per_query(args.T_per_query)
    complete_qrel_queries = args.complete_qrel_queries

    if args.over_write_T:
        Ts = dict(zip(results.keys(), [args.over_write_T]*len(results))) # overwrite Ts to the supplied constant value

    inst_eval(results, qrels, Ts, find_max_graded_label(qrels), complete_qrel_queries)





