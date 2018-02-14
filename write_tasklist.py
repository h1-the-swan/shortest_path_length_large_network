import sys, os, time
from glob import glob
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


def get_basename(fname):
    b = os.path.basename(fname)
    b = os.path.splitext(b)[0]
    return b

def output_one_line(path_to_script, 
                    path_to_graph, 
                    path_to_pairs, 
                    output_dirname, 
                    log_dirname, 
                    start_idx, 
                    num=80):
    end_idx = start_idx + num
    output_fname = os.path.join(output_dirname, "shortest_path_lengths_samples_{}-{}.tsv".format(start_idx, end_idx))
    log_fname = os.path.join(log_dirname, "shortest_path_lengths_samples_{}-{}.log".format(start_idx, end_idx))

    # build the command as a list of strings, which can be concatenated at the end
    out = ['python']
    out.append(path_to_script)
    out.append(path_to_graph)
    out.append(path_to_pairs)
    out.append("-o {}".format(output_fname))
    out.append("--start {}".format(start_idx))
    out.append("--num {}".format(num))
    out.append('--debug')
    out.append('>& {}'.format(log_fname))  # output stdout and stderr to a file

    out = ' '.join(out)
    return out


def main(args):
    script = os.path.abspath(args.script)
    script_dirname = os.path.split(script)[0]
    outfname = args.taskfile
    if outfname:
        outfname = os.path.abspath(outfname)
    else:
        outfname = os.path.join(script_dirname, "tasklist_shortest_path_lengths.txt")
    if os.path.exists(outfname):
        raise RuntimeError("path {} already exists".format(outfname))

    graph_fname = os.path.abspath(args.graph)
    pairs_fname = os.path.abspath(args.pairs)

    outdir = args.outdir
    if outdir:
        outdir = os.path.abspath(outdir)
    else:
        outdir = os.path.join(script_dirname, "output")

    logdir = args.logdir
    if logdir:
        logdir = os.path.abspath(logdir)
    else:
        logdir = os.path.join(script_dirname, "logs")


    # # only do a certain number for now
    # stop_after = 2
    logger.info("writing to {}".format(outfname))
    cur_idx = args.start
    end_idx = args.end
    step = args.num
    with open(outfname, 'w') as outf:
        number_written = 0
        while True:
            line = output_one_line(script,
                                    graph_fname,
                                    pairs_fname,
                                    outdir,
                                    logdir,
                                    cur_idx,
                                    num=step)
            if line:
                outf.write(line)
                outf.write('\n')
                number_written += 1
            # if number_written == stop_after:
            #     break
            cur_idx = cur_idx + step
            if cur_idx >= end_idx:
                break


if __name__ == "__main__":
    total_start = timer()
    logger = logging.getLogger(__name__)
    logger.info(" ".join(sys.argv))
    logger.info( '{:%Y-%m-%d %H:%M:%S}'.format(datetime.now()) )
    import argparse
    parser = argparse.ArgumentParser(description="write tasklist for use with parallel-sql")
    parser.add_argument("script", help="script file for each task to run")
    parser.add_argument("graph", help="network graph (Pajek .net file)")
    parser.add_argument("pairs", help="tsv file with pairs samples")
    parser.add_argument("-o", "--outdir", help="output directory")
    parser.add_argument("-l", "--logdir", help="logfiles directory")
    parser.add_argument("--taskfile", help="path to the tasklist file written by this program")
    parser.add_argument("--start", type=int, default=0, help="index of the sample pair to start for the first job")
    parser.add_argument("--num", type=int, default=80, help="number of pairs to calculate for each job")
    parser.add_argument("--end", type=int, default=153800, help="index to end")
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
