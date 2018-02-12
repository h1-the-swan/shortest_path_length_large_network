Try to get shortest path length on large network

2018-02-12
Running on HPC:
background jobs are killed after 4 hours.
Based on tests, It looks like we can calculate about 90 shortest path lengths in 4 hours (including the time it takes to load the network).
Maybe try doing 80, to be safe.
There are 16 categories with >= 500 papers. =256 category pairs.
With 500 samples per pair: 128,000 shortest path length calculations.
=1,600 jobs on HPC
