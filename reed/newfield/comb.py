#!/usr/bin/env python
# -#- coding: utf-8 -#-
'''
Created on Apr 14, 2014

@author: ajaniv

Problem description:
Assume the US dollar is available in denominations of
$100, $50, $20, $10, $5, $1, $0.25, $0.10, $0.05 and $0.01.
Write a function to return the number of different ways to
exactly represent an arbitrary value less than $1,000.00 using
any number or combination of these denominations.


This was executed on a MacBook Pro 2.9 GHz Intel Core i7, 8GB 1600 MHZ RAM
using Python 2.76

There is likely a misunderstanding of the requirements on my part or the
implementation approach is flawed.  Without setting limits to the combination
with replacement, the computation is very  inefficient.  Without
a reference implementation and measurements, and clarifications on
the requirements, it is somewhat tricky to identify the root cause
for the poor performance.

> comb.py -l 30 .10 .20 .50 1.00  5.00 10.00 25.00 50.00 100 500 999.99
Using combination with replacement limit: 30.
Computing for the following targets: [0.1, 0.2, 0.5, 1.0, 5.0, 10.0, 25.0,
    50.0, 100.0, 500.0, 999.99].

Target         comb_count(N)         seconds
==========     =============         =======
      0.10                4        0.000232
      0.20                9        0.000931
      0.50               39        0.02792
      1.00              110        0.1896
      5.00              398        1.127
     10.00              533        6.069
     25.00             1462        28.39
     50.00             2315        116.9
    100.00             4281        455.0
    500.00             7526        471.0
    999.99               34        474.1


Caution: only the first two targets have a complete set of results
with the current implementation using the combination limit approach
to constrain the number of computations.

Thoughts on  performance improvements:
- Implement in C++
- Re-engineer the algorithm (likely at the cost of readability.
  Without a reference implementation it is somewhat tricky.
- Pre-compute the results for all possible numbers < 1000, and cache
- Using grid of compute engines
'''

import argparse
import time
import unittest
from itertools import combinations_with_replacement

MAX_TARGET = 1000
MIN_TARGET = 0
MAX_LIMIT = 50
EPSILON = .0001


class TestComb(unittest.TestCase):

    def test_comb(self):
        target = .10
        epsilon = .00001

        expected_results = [(0.1,), (0.05, 0.05),
                    (0.05, 0.01, 0.01, 0.01, 0.01, 0.01),
                    (0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01,
                        0.01, 0.01, 0.01)]
        denoms = [.10,  0.05, 0.01]
        smallest = min(denoms)
        range_end = int(target / smallest) + 1
        results = [comb for i in range(1, range_end)
                  for comb in combinations_with_replacement(denoms, i)
                  if abs(sum(comb) - target) < epsilon]
        self.assertEqual(results, expected_results)
        self.assertEqual(len(results), len(expected_results))
        self.assertEqual(comb_count(denoms, target, epsilon),
                         len(expected_results))


def comb_count(values, target, limit=None, epsilon=None):
    """
    Combination with replacement counter for
    a set of values

    The method was profiled using python profiler, and efforts
    to improve the performance failed.  Had to introduce concept
    of limit to the combination of replacement.  Replacing the 'sum'
    function with a for loop resulted in worse performance.

    Distributing the computation over a network grid would
    improve performance depending on the number of compute engines,
    network task distribution cost, and the granularity of the task.
    Coarse grained tasking could be performed per each 'i' value, or
    at the level of the 'combinations_with_replacement' calls
    """
    if (values == None or not len(values) or target is None
        or target <= 0):
        raise ValueError

    epsilon = epsilon or EPSILON
    limit = limit or MAX_LIMIT
    values = list({value for value in values if value <= target})
    values.sort()
    smallest = min(values)
    range_end = min(limit, int(target / smallest) + 1)
    count = 0
    for i in range(1, range_end):
        for comb in combinations_with_replacement(values, i):
            if abs(sum(comb) - target) < epsilon:
                count += 1
    return count


def calc():
    parser = argparse.ArgumentParser(description='Denomination combinations.')
    parser.add_argument('targets', metavar='N', type=float, nargs='+',
                       help='Target number (0 < N < 1000)')
    parser.add_argument('-l', '--limit', default=MAX_LIMIT, type=int,
                        help='combination with replacement limit')

    args = parser.parse_args()
    denoms = [100, 50, 20, 10, 5, 1, 0.25, .10, 0.05, 0.01]

    limit = args.limit
    if limit > MAX_LIMIT:
        raise ValueError("invalid limit value %s > %s " % (limit, MAX_LIMIT))

    print "Using combination with replacement limit: %s." % limit
    print "Computing for the following targets: %s.\n" % args.targets

    print "Target", "\t" * 2, "comb_count(N)", "\t" * 2,  "seconds"
    print "=" * 10, "\t" * 1, "=" * 13, "\t" * 2, "=" * 7

    for target in args.targets:
        if target >= MAX_TARGET or target <= MIN_TARGET:
            print 'ignoring invalid target: ', target
            continue
        start = time.clock()
        result = comb_count(denoms, target, limit=limit, epsilon=EPSILON)
        end = time.clock()
        print "{:>10.2f}\t{:>13}\t\t{:.4}".format(
                    target, result, end - start)

if __name__ == '__main__':
    calc()
