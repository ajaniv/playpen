#!/usr/bin/env python
# -#- coding: utf-8 -#-
"""
Created on Apr 14, 2014

@author: ajaniv
Problem description:
Determine the sum of all prime numbers less than an
input number  N (the input number will be at most 10,000,000).

primes are integers greater than one with no positive divisors.


When ran with the following arguments:

>prime_sum.py -1 0 1 2  100  1000 10000 100000 1000000  10000000


Results produced:
N                  sum_primes(N)         seconds
==========         =============         =======
        -1                    0            4e-06
         0                    0            2e-06
         1                    0            0.0
         2                    2            3e-06
       100                 1060            0.000119
      1000                76127            0.001544
     10000              5736396            0.02531
    100000            454396537            0.3176
   1000000          37550402023            7.034
  10000000        3203324994356            206.0





How to improve performance:
- Implement in C++
- Implement in C++ using multi threading for large numbers.  In python, because
  of the GIL lock, CPU bound threads are effectively single threaded
- Using python and a process pool executing locally for large numbers
- Consider caching results if the method is frequently invoked with
  the same arguments.
"""

import argparse
import time
import math
import unittest

MAX_NUMBER = 10000000


class TestPrime(unittest.TestCase):
    ref_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37,
                    41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]

    input_number = 100

    def test_prime(self):
        primes = [num for num in range(self.input_number) if is_prime(num)]
        self.assertEqual(self.ref_primes, primes)

    def test_invalid_prime(self):
        for num in (-1, 0, 1):
            self.assertFalse(is_prime(num))

    def test_sum_primes(self):
        expected_sum = sum(self.ref_primes)
        self.assertEqual(expected_sum, sum_primes(self.input_number))

    def test_invalid_sum_primes(self):
        for num in (-1, 0, 1):
            self.assertEqual(0, sum_primes(num))


def is_prime(num):
    """
    Sieve of Eratosthenes: check only
    up to the floor of the square root of the number.
    """
    if num <= 1:
        return False
    for j in range(2, int(math.sqrt(num) + 1)):
        if (num % j) == 0:
            return False
    return True


def sum_primes(input_number):
    """
    Sum all prime numbers less than  input number
    """

    total = 0
    if input_number <= 1:
        return 0

    if input_number > MAX_NUMBER:
        raise ValueError("input number %s > %s" % (input_number, MAX_NUMBER))

    # processing odd numbers only
    for num in range(3, input_number, 2):
        if is_prime(num):
            total += num

    # compensating for starting by 2
    return total + 2


def calc():
    """
    Process user input, validate, perform sum of primes calculation
    """
    parser = argparse.ArgumentParser(description='Sum prime numbers.')
    parser.add_argument('numbers', metavar='N', type=int, nargs='+',
                       help='boundary input number')

    args = parser.parse_args()
    print "Computing for the following targets: %s." % args.numbers
    print "N", "\t" * 3, "sum_primes(N)", "\t\t",  "seconds"
    print "=" * 10, "\t" * 2, "=" * 13, "\t\t", "=" * 7
    for number in args.numbers:
        if number > MAX_NUMBER:
            print "skipping input number %s > %s" % (number, MAX_NUMBER)
            continue
        start = time.clock()
        result = sum_primes(number)
        end = time.clock()
        print "{:10}\t\t{:13}\t\t{:.4}".format(
                    number, result, end - start)

if __name__ == '__main__':
    calc()
