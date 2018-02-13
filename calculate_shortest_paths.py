import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

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
        

def main(args):
    graph_fname = os.path.abspath(args.graph)
    start = timer()
    logger.debug("loading graph from file: {}...".format(graph_fname))
    # G = load_graph(graph_fname)
    logger.debug("done loading graph. took {}".format(format_timespan(timer()-start)))

    output_fname = os.path.abspath(args.out)
    logger.debug("opening output file for writing: {}".format(output_fname))
    outf = open(output_fname, 'w')

    start_idx = args.start
    end_idx = start_idx + args.num
    logger.debug("starting with pair number {}. ending with (and not including) pair number {}".format(start_idx, end_idx))
    pairs = []

    # collect the pairs we will calculate shortest path for
    with open(args.pairs, 'r') as f:
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
    logger.debug("starting shortest path length calculations for {} pairs...".format(len(pairs)))
    for pair in pairs:
        start_pair = timer()
        sp_length = get_shortest_path_length_for_one_pair(G, pair.source_mag_id, pair.target_mag_id)
        output_row = [str(pair.source_arxiv_id, pair.target_arxiv_id, str(sp_length))]
        outf.write("\t".join(output_row))
        outf.write("\n")
        logger.debug("done calculating shortest path for {} to {}. sp_length: {}. took {}".format(output_row[0], output_row[1], output_row[2], timer()-start_pair))
    logger.debug("done calculating shortest paths for {} pairs. took {}".format(len(pairs), timer()-start))


    outf.close()

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="given a network (pajek file) and a list of node pairs, calculate the shortest path lengths for a subset of those node pairs", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("graph", help="network graph (Pajek .net file)")
    parser.add_argument("pairs", help="tsv file with pairs samples")
    parser.add_argument("-o", "--out", help="output file (tsv). contains 3 columns: source_arxiv_id, target_arxiv_id, shortest_path_length")
    parser.add_argument("--start", type=int, default=0, help="index of the sample pair to start")
    parser.add_argument("--num", type=int, default=80, help="number of pairs to calculate (starting from --start)")
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
