import sys, os, time
from datetime import datetime
from timeit import default_timer as timer
try:
    from humanfriendly import format_timespan
except ImportError:
    def format_timespan(seconds):
        return "{:.2f} seconds".format(seconds)

import pandas as pd
import numpy as np

import logging
logging.basicConfig(format='%(asctime)s %(name)s.%(lineno)d %(levelname)s : %(message)s',
        datefmt="%H:%M:%S",
        level=logging.INFO)
# logger = logging.getLogger(__name__)
logger = logging.getLogger('__main__').getChild(__name__)

def main(args):
    df = pd.read_csv(args.input, sep=args.sep, dtype=str)
    gb = df.groupby(args.category_colname).filter(lambda x: len(x) > args.min_papers).groupby(args.category_colname)
    random_state = np.random.RandomState(args.seed)
    outf = open(args.output, 'w')
    for name1, indices1 in gb.groups.items():
        for name2, indices2 in gb.groups.items():
            pairs_str = "# {}{}{}".format(name1, '\t', name2)
            outf.write(pairs_str)
            outf.write('\n')
            sample_pairs = set()
            while len(sample_pairs) < args.sample_size:
                source = random_state.choice(indices1)
                target = random_state.choice(indices2)
                pair = (source, target)
                sample_pairs.add(pair)
                outf.write('\t'.join([df.loc[source]['arxiv_id'], df.loc[source]['mag_id'], df.loc[target]['arxiv_id'], df.loc[target]['mag_id']]))
                outf.write('\n')
    outf.close()

if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="get sample pairs by broad category", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input", help="filename for input (TSV)")
    parser.add_argument("output", help="filename for output (TSV)")
    parser.add_argument("--sep", default='\t', help="delimiter for the input file (default: tab)")
    parser.add_argument("--category-colname", default='category_broad', help="column name for the category")
    parser.add_argument("--min-papers", type=int, default=500, help="categories with fewer than this many papers will be filtered out")
    parser.add_argument("--seed", type=int, default=99, help="random seed")
    parser.add_argument("--sample-size", type=int, default=500, help="number of sample pairs for each pair of categories")
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
