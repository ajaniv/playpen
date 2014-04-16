#!/usr/bin/env python
# -#- coding: utf-8 -#-
'''
Created on Apr 15, 2014

@author: ajaniv

Problem Description:
Given a csv format table of telephone calls;
each call is on a line of the format
“calling #, called #”. Define friends as any two people who have talked,
and acquaintances as any two people who are not friends, but share a friend.
Thus, if A talks to B, and C talks to B, then A and B are friends, A and C
are acquaintances.  Find who has the most acquaintances.
The table will have at most 1,000,000 entries, and the phone numbers will
be integers with at most 15 digits.


Issue: without a reference data set for testing with expected results,
test data generation (i.e. 1M rows) is tricky, and requires usage of
random numbers, and building relationships between them.

> acquaintances.py  calls.csv calls.csv
Computing for the following files: ['calls.csv', 'calls.csv'].
file                 max     acquaintances             seconds
===============         ===     ===============         =======
calls.csv               2    [6099241931, 2014638884]    0.001938
calls.csv               2    [6099241931, 2014638884]    0.000886


'''
import os.path
import itertools
import collections
import argparse
import time
import csv
import unittest

DEFAULT_FILE_NAME = 'calls.csv'


class TestAcquaintances(unittest.TestCase):

    def test_csv(self):
        processor = CallProcessor('calls.csv')
        processor.load()
        self.assertEqual(len(processor.calls), 2)
        self.assertEqual(processor.max_acquaintances(),
                          (2, [6099241931, 2014638884]))


class CallProcessor(object):
    def __init__(self, file_name):
        self.file_name = file_name
        self.calls = collections.defaultdict(list)
        self.aquaintances = collections.defaultdict(set)

    def load(self):
        with open(self.file_name, 'rb') as phone_file:
            has_header = csv.Sniffer().has_header(phone_file.read(1024))
            phone_file.seek(0)
            incsv = csv.reader(phone_file, delimiter=',')
            if has_header:
                next(incsv)  # skip header row
            self.build_calls(incsv)

    def run(self):
        self.load()
        return self.max_acquaintances()

    def build_calls(self, csv_handle):
        for row in csv_handle:
            try:
                calling, called = map(int, row)
                if calling == called:
                    raise ValueError(
                        'equal calling and called (%s,%s).' % (calling,
                                                               called))
                self.calls[calling].append(called)
                self.aquaintances[called].add(calling)
            except ValueError as ex:
                print 'invalid values; skipping row %s; %s.' % (row, ex)

    def max_acquaintances(self):
        results = collections.defaultdict(int)

        def max_results():
            """
            Return the list of  one or more max_acquaintances
            """
            max_map = collections.defaultdict(list)
            for key, value in results.items():
                max_map[value].append(key)
            max_key = max(max_map.keys())
            return max_key, max_map[max_key]

        for called, callings in self.aquaintances.items():  # @UnusedVariable
            if len(callings) > 1:
                comb = list(itertools.combinations(callings, 2))
                acq_count = (len(comb) / len(callings)) + 1
                for calling in callings:
                    results[calling] += acq_count

        return max_results()


def calc():
    """
    Process user input, validate, max acquaintances computation
    """
    parser = argparse.ArgumentParser(
            description='Find max acquaintance/acquaintances.')
    parser.add_argument('files', metavar='file',
            type=str,
            nargs='+',
            help='csv files with call data')

    args = parser.parse_args()

    print "Computing for the following files: %s." % args.files
    print "file", "\t" * 4, "max", "\t" * 1, "acquaintances", "\t" * 3, "seconds"
    print "=" * 15, "\t" * 2, "=" * 3, "\t", "=" * 15, "\t" * 2, "=" * 7

    for file_name in args.files:
        if not os.path.isfile(file_name):
            print "skipping file %s " % (file_name)
            continue
        start = time.clock()
        processor = CallProcessor(file_name)
        acq_count, acq_phones = processor.run()
        end = time.clock()
        print "{:10}\t\t\t{:3}\t{:13}\t{:.4}".format(
                    file_name, acq_count, acq_phones, end - start)

if __name__ == '__main__':
    calc()
