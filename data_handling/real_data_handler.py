import datetime

import pandas as pd
import json

def fetch_ctr_seq_time_100k():
    filename = "data/ctr_seq_time_100k_mapped"
    with open(filename + ".json", 'r') as handle:
        traces_dict = json.load(handle)
    for trace in traces_dict:
        ctr_trace = traces_dict[trace]["trace_variant"]["original_trace"]
        return [trace, ctr_trace]

def get_n_items(dict_name):
    spl_char = '_n'
    first_part = dict_name.split(spl_char, 1)[1]
    spl_char = '_m'
    return first_part.split(spl_char, 1)[0]

def fetch_simple_seq(name):
    filename = name
    with open(filename + ".json", 'r') as handle:
        traces_dict = json.load(handle)
    for trace in traces_dict:
        actual_trace = traces_dict[trace]["trace variants"]["original-trace"]
        return [trace, actual_trace]

def count_nodes(set, single):
        """returns number of distinct nodes (hosts) in the sequence"""

        counter = dict()
        for item in set:
            if single:
                if item in counter:
                    counter[item] += 1
                else:
                    counter[item] = 0
            else:
                if item[0] in counter:
                    counter[item[0]] += 1
                else:
                    counter[item[0]] = 0
                if item[1] in counter:
                    counter[item[1]] += 1
                else:
                    counter[item[1]] = 0
        return len(counter)

def get_metrics(sequence, single=False):
    n_nodes = count_nodes(sequence, single=single)
    n_req = len(sequence)
    return [n_nodes, n_req]