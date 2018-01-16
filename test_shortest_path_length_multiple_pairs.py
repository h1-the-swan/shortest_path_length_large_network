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

import pandas as pd

def load_graph(fname):
    G = igraph.Graph.Read_Pajek(fname)
    return G

def get_vertex_seq_id(G, original_id):
    """gets the igraph vertex sequence id for a given node id"""
    try:
        return G.vs.find(id=str(original_id)).index
    except ValueError:
        return None


def main(args):
    fname_pairs = os.path.abspath(args.pairs)
    logger.debug("loading pairs from file: {}".format(fname_pairs))
    pairs = pd.read_table(fname_pairs)
    logger.debug("there are {} pairs".format(len(pairs)))

    fname = os.path.abspath(args.input)
    start = timer()
    logger.debug("loading graph from file: {}".format(fname))
    # G = load_graph(fname, delimiter=args.sep, directed=False, nodetype=int)
    G = load_graph(fname)
    logger.debug ("done. took {}".format(format_timespan(timer()-start)))

    start_testpairs = timer()
    logger.debug("getting shortest path length between all pairs...")

    times = []
    for name, row in pairs.iterrows():
        start = timer()
        source_igraph_id = get_vertex_seq_id(G, row.source_mag_id)
        target_igraph_id = get_vertex_seq_id(G, row.target_mag_id)
        logger.info("source: arxiv_id {}  |  mag_id {}  |  igraph_id {}".format(row.source_arxiv_id, row.source_mag_id, source_igraph_id))
        logger.info("target: arxiv_id {}  |  mag_id {}  |  igraph_id {}".format(row.target_arxiv_id, row.target_mag_id, target_igraph_id))
        if ( not source_igraph_id ) or ( not target_igraph_id ):
            logger.info("source/target nodes not identified. skipping...")
        else:
            sp_length = G.shortest_paths(source=source_igraph_id, target=target_igraph_id, mode='ALL')
            logger.info("shortest path length: {}".format(sp_length))
            logger.debug("calculating this pair took {}".format(format_timespan(timer()-start)))
        logger.info("")
        times.append(timer()-start)
        # mode='ALL' means consider the graph as undirected
    logger.debug("done testing all pairs. took {}".format(format_timespan(timer()-start_testpairs)))
    logger.debug("average time per pair: {}".format(format_timespan(sum(times) / len(times))))
    # with open('hepth_sample_pairs_times.txt', 'w') as times_outf:
    #     for t in times:
    #         times_outf.write(str(t))
    #         times_outf.write('\n')


if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="test calculating shortest path length for multiple node pairs")
    parser.add_argument("input", help="file containing the network (.net pajek file)")
    parser.add_argument("pairs", help="tsv file containing the node pairs")
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
