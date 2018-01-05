import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

import networkx as nx

def load_graph(fname, delimiter='\t', directed=False, nodetype=int):
    if directed is True:
        G = nx.DiGraph()
    else:
        G = nx.Graph()
    G = nx.read_edgelist(fname, delimiter=delimiter, create_using=G, nodetype=nodetype)
    return G


def main(args):
    fname = os.path.abspath(args.edgelist)
    start = timer()
    logger.debug("loading graph from file: {}".format(fname))
    G = load_graph(fname, delimiter=args.sep, directed=False, nodetype=int)
    logger.debug ("done. took {}".format(format_timespan(timer()-start)))

    start = timer()
    logger.debug("getting shortest path betweeen papers: {} -- {}".format(args.id1, args.id2))
    sp_length = nx.shortest_path_length(G, source=args.id1, target=args.id2)
    logger.debug("done. took {}".format(format_timespan(timer()-start)))

    print("Shortest path length between papers {} and {}: {}".format(args.id1, args.id2, sp_length))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="test shortest path length. takes as input the full edgelist, then the paper ids of two papers to find the shortest path length between")
    parser.add_argument("edgelist", help="file containing the edgelist")
    parser.add_argument("id1", type=int, help="first paper id (integer)")
    parser.add_argument("id2", type=int, help="second paper id (integer)")
    parser.add_argument("--sep", default='\t', help="delimiter for the edgelist file (default: tab)")
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
