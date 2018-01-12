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

import igraph

def load_graph(fname):
    G = igraph.Graph.Read_Pajek(fname)
    return G

def get_vertex_seq_id(G, original_id):
    """gets the igraph vertex sequence id for a given node id"""
    return G.vs.find(id=str(original_id)).index


def main(args):
    fname = os.path.abspath(args.input)
    start = timer()
    logger.debug("loading graph from file: {}".format(fname))
    # G = load_graph(fname, delimiter=args.sep, directed=False, nodetype=int)
    G = load_graph(fname)
    logger.debug ("done. took {}".format(format_timespan(timer()-start)))

    start = timer()
    logger.debug("getting shortest path length betweeen papers: {} -- {}".format(args.id1, args.id2))
    igraph_id1 = get_vertex_seq_id(G, args.id1)
    igraph_id2 = get_vertex_seq_id(G, args.id2)
    logger.debug("the igraph vertex sequence ids for these papers are: {} -- {}".format(igraph_id1, igraph_id2))
    sp_length = G.shortest_paths(source=igraph_id1, target=igraph_id2, mode='ALL')
    # mode='ALL' means consider the graph as undirected
    logger.debug("done. took {}".format(format_timespan(timer()-start)))

    print("Shortest path length between papers {} and {}: {}".format(args.id1, args.id2, sp_length))

    start = timer()
    logger.debug("getting shortest path betweeen papers: {} -- {}".format(args.id1, args.id2))
    sp_path = G.get_shortest_paths(igraph_id1, igraph_id2, mode='ALL')
    # mode='ALL' means consider the graph as undirected
    logger.debug("done. took {}".format(format_timespan(timer()-start)))
    print("Shortest path between papers {} and {}: {}".format(args.id1, args.id2, sp_path))

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="test shortest path length. takes as input the full network (as a pajek file), then the paper ids of two papers to find the shortest path length between")
    parser.add_argument("input", help="file containing the network (.net pajek file)")
    parser.add_argument("id1", type=int, help="first paper id (integer)")
    parser.add_argument("id2", type=int, help="second paper id (integer)")
    # parser.add_argument("--sep", default='\t', help="delimiter for the edgelist file (default: tab)")
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
