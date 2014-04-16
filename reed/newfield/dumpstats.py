import pstats
pstats.Stats('comb.stat').strip_dirs().sort_stats("cumulative").print_stats()
