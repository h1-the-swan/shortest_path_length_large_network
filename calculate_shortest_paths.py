import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

from multiprocessing import Pool, cpu_count
from shortest_path_length_utils import load_graph, get_shortest_path_length_for_one_pair

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

class Pair(object):
    def __init__(self, source_arxiv_id, source_mag_id, target_arxiv_id, target_mag_id):
        self.source_arxiv_id = source_arxiv_id
        self.source_mag_id = source_mag_id
        self.target_arxiv_id = target_arxiv_id
        self.target_mag_id = target_mag_id

def calculate_paths_for_range_of_pairs(G, out, start, num, pairs):
    output_fname = os.path.abspath(out)
    logger.debug("opening output file for writing: {}".format(output_fname))
    outf = open(output_fname, 'w')

    start_idx = start
    end_idx = start_idx + num
    logger.debug("starting with pair number {}. ending with (and not including) pair number {}".format(start_idx, end_idx))
    pairs = []

    # collect the pairs we will calculate shortest path for
    with open(pairs, 'r') as f:
        pair_idx = 0
        for line in f:
            if line[0] == "#":
                # ignore comments
                continue
            if pair_idx == end_idx:
                break
            if pair_idx >= start_idx:
                line = line.strip().split('\t')
                pair = Pair(*line)
                pairs.append(pair)
            pair_idx += 1

    # do the calculations and write to file
    start = timer()
    logger.debug("starting shortest path length calculations for {} pairs (starting with idx {})...".format(len(pairs), start_idx))
    for pair in pairs:
        start_pair = timer()
        sp_length = get_shortest_path_length_for_one_pair(G, pair.source_mag_id, pair.target_mag_id)
        output_row = [str(pair.source_arxiv_id), str(pair.target_arxiv_id), str(sp_length)]
        outf.write("\t".join(output_row))
        outf.write("\n")
        logger.debug("done calculating shortest path for {} to {}. sp_length: {}. took {}".format(output_row[0], output_row[1], output_row[2], format_timespan(timer()-start_pair)))
    logger.debug("done calculating shortest paths for {} pairs (starting with idx {}). took {}".format(len(pairs), start_idx, format_timespan(timer()-start)))

    outf.close()
        

def unpack_args_for_worker(arg_dict):
    calculate_paths_for_range_of_pairs(**arg_dict)

def main(args):
    graph_fname = os.path.abspath(args.graph)
    start = timer()
    logger.debug("loading graph from file: {}...".format(graph_fname))
    G = load_graph(graph_fname)
    logger.debug("done loading graph. took {}".format(format_timespan(timer()-start)))

    outdir = os.path.abspath(args.outdir)

    num_cpus = args.processes

    arg_dicts = []

    # split the data into bins for parallel processing
    cur_idx = args.start
    step = args.num
    for i in range(num_cpus):
        end_idx = cur_idx + step
        output_fname = os.path.join(outdir, "shortest_path_lengths_samples_{}-{}.tsv".format(cur_idx, end_idx))
        this_arg_dict = {
            'G': G,
            'out': output_fname,
            'start': cur_idx,
            'num': step,
            'pairs': args.pairs
        }
        arg_dicts.append(this_arg_dict)
        cur_idx = end_idx

    logger.debug("starting a pool of workers with {} processes".format(num_cpus))
    pool = Pool(processes=num_cpus)
    logger.debug("mapping {} processes to the pool".format(len(arg_dicts)))
    pool.map(unpack_args_for_worker, arg_dicts)



if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given a network (pajek file) and a list of node pairs, calculate the shortest path lengths for a subset of those node pairs", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("graph", help="network graph (Pajek .net file)")
    parser.add_argument("pairs", help="tsv file with pairs samples")
    parser.add_argument("-o", "--outdir", help="output directory. output files are TSV. They contain 3 columns: source_arxiv_id, target_arxiv_id, shortest_path_length")
    parser.add_argument("--start", type=int, default=0, help="index of the sample pair to start")
    parser.add_argument("--num", type=int, default=80, help="number of pairs to calculate (starting from --start)")
    parser.add_argument("--processes", type=int, default=15, help="number of processes to run at a time")
    parser.add_argument("--debug", action='store_true', help="output debugging info")
    global args
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('debug mode is on')
    else:
        logger.setLevel(logging.INFO)
    main(args)
    total_end = timer()
    logger.info('all finished. total time: {}'.format(format_timespan(total_end-total_start)))
