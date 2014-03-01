#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
All unit tests for vSummarize should be contained here.
"""
__title__ = 'vSummarize'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import sys
import os
import unittest
import time

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.join(TEST_DIR, '..')

# Tests is a separate module, insert parent dir manually
sys.path.insert(0, PARENT_DIR)

from backend import algorithm
from backend import youtube


def print_test(method):
    """
    Utility method for print verbalizing test suite, prints out
    time taken for test and functions name, and status.
    """
    def run(*args, **kw):
        ts = time.time()
        print '\ttesting function %r' % method.__name__
        method(*args, **kw)
        te = time.time()
        print '\t[OK] in %r %2.2f sec' % (method.__name__, te-ts)
    return run

class GeneralUnitTestCases(unittest.TestCase):
    def runTest(self):
        self.TIMESTAMPS = [u'1:46', u'1:46', u'1:51', u'00:40', u'1:43',
                           u'1:35', u'1:44', u'1:47', u'2:22', u'02:48',
                           u'1:21', u'1:32', u'1:39']
        self.DURATION = '197'
        self.client = youtube.get_client()
        self.video_id = 'p5HXQ1HFDgA'

        self.conversion_test()
        self.convert_timestamps_test()
        self.get_timestamps_test()
        self.sort_timestamp_test()
        self.get_hotspot_test()
        self.expand_hotspot_test()
        self.video_summarize_test()
        # self.video_api_summarize_test()

    @print_test
    def conversion_test(self):
        assert algorithm.convert_to_seconds(u'1:40') == 100

    @print_test
    def get_timestamps_test(self):
        timestamps = youtube.get_timestamp_list(self.client, self.video_id)
        print timestamps
        duration_seconds = youtube.get_duration(self.client, self.video_id)
        assert self.DURATION == duration_seconds

    @print_test
    def sort_timestamp_test(self):
        unique_times = algorithm.unique_timestamps(self.TIMESTAMPS)
        self.sorted_times = algorithm.sort_timestamps(unique_times)
        SORTED_TIMES = [u'00:40', u'1:21', u'1:32', u'1:35', u'1:39',
                u'1:43', u'1:44', u'1:46', u'1:47', u'1:51', u'2:22', u'02:48']
        assert self.sorted_times == SORTED_TIMES

    @print_test
    def get_hotspot_test(self):
        HOTSPOTS = [(u'00:40', 1), (u'1:21', 1), (u'1:32', 3), (u'1:43', 4),
                (u'1:51', 1), (u'2:22', 1), (u'02:48', 1)]
        self.hotspots = algorithm.get_hotspots(self.sorted_times, self.DURATION)
        assert self.hotspots == HOTSPOTS

    @print_test
    def convert_timestamps_test(self):
        t1 = 72
        t2 = -5
        assert algorithm.convert_to_timestamp(t1) == '00:01:12'
        assert algorithm.convert_to_timestamp(t2) == '00:00:00'

    @print_test
    def expand_hotspot_test(self):
        self.HOTCLIPS = [(37, 43), (78, 84), (89, 95), (100, 106), (108, 114),
                (139, 145), (165, 171)]
        self.hotclips = algorithm.expand_hotspots(self.hotspots, self.DURATION)
        assert self.hotclips == self.HOTCLIPS

    @print_test
    def video_summarize_test(self):
        hotclips = algorithm.get_clips(self.TIMESTAMPS, self.DURATION)
        print 'the hotclips of this video are', hotclips
        assert hotclips == self.HOTCLIPS

    """
    @print_test
    def video_api_summarize_test(self):
        data = vsummarize.summarize('http://www.youtube.com/watch?v=8pvHZ4ddR-4',
                output='thegame.mp4')

        print 'hot clips', data.hot_clips
        print 'timestamps', data.timestamps
        print 'duration', data.duration

        assert len(data.hot_clips) != 0
        assert len(data.timestamps) != 0
        assert data.duration is not None
    """

if __name__ == '__main__':
    # unittest.main() # run all units and their cases
    suite = unittest.TestSuite()
    suite.addTest(GeneralUnitTestCases())
    unittest.TextTestRunner().run(suite)
