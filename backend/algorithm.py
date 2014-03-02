#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__title__ = 'vSummarize'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import time
import random


def all_to_timestamp(second_tuples):
    """
    Converts a list of 2-tuples of seconds into a list of 2-tuples of timestamps.
    """
    return [(convert_to_timestamp(tup[0]), convert_to_timestamp(tup[1]))
            for tup in second_tuples]

def convert_to_timestamp(seconds):
    """
    Converts an integer into a string 'HH:MM:SS'.
    We differ a bit from python's standard time library
    in that if a number is negative, instead of reversing
    back into the 24hr mark, we return 00:00:00.
    """
    if seconds < 0:
        return '0:00'

    tt = time.strftime('%H:%M:%S', time.gmtime(seconds))
    if tt[:2] == '00':
        tt = tt[3:]  # slice off leading ':' also
    if tt[:1] == '0':
        tt = tt[1:]
    return tt

def convert_to_seconds(timestamp):
    """
    Takes a string timestamp: [\d]{0,1}\d:\d\d and
    returns an int representing the number of seconds.
    """
    if ':' not in timestamp:
        raise Exception('Funky shit happening w/ timestamps')
    minutes = 0
    seconds = 0
    tsplit = timestamp.split(':')
    num_colon = timestamp.count(':')
    if num_colon == 1:
        seconds = int(tsplit[1])
        minutes = int(tsplit[0])
        return (minutes * 60) + seconds
    elif num_colon == 2:
        hours = int(tsplit[0])
        minutes = int(tsplit[1])
        seconds = int(tsplit[2])
        return (hours * 3600) + (minutes * 60) + seconds
    raise Exception('Funky shit happening w/ timestamps')

def unique_timestamps(timestamps):
    """
    Remove duplicate timestamps.
    """
    return list(set(timestamps))

def sort_timestamps(timestamps):
    """
    Sort string timestamps by earliest-latest order
    """
    return sorted(timestamps, key=lambda num: convert_to_seconds(num))

def sort_seconds(timestamps):
    """
    Sorts a list of 2-tuples by their first element
    """
    return sorted(timestamps, key=lambda tup: tup[0])

def hotness_delta(video_duration):
    """
    Hotness delta is the number of seconds apart where
    two timestamps are considered to be referencing same event.

    Alongside the above, we are also using delta to decide by
    how many seconds to expand a hotspot time.
    A delta of 7 and hotspots of 0:30 and 1:45 would generate
    hotspot clips of (0:23, 0:37), (1:38, 1:52). We add the
    delta to both directions.

    For us, this is dependent on the length of the video. A
    longer video will have a longer hotness delta.
    """
    if not isinstance(video_duration, int):
        video_duration = int(video_duration)
    if video_duration < 10:
        return 2
    elif video_duration < 120:
        return 8
    elif video_duration < 300:
        return 12
    return 15

def get_hotspots(timestamps, video_duration):
    """
    We will now compute hotspot points along with their scores;
    a hotspot point is a timestamp point with a higher proportion
    of other timestamps close to it. If we can't manage to extract
    a ton of timestamps, chances are that the hotspot points will
    just be a list of unique timestamps.

    We will compute a time delta d s.t. if two timestamps are less
    than d seconds away from eachother, they are considered the same
    time and their scores are boosted.

    Hotspots are a list of tuples X, with X(0) being a time and X(1)
    being the "hit counter" hotness of that time.
    """
    sorted_times = sort_timestamps(timestamps)
    hit_counter = {time:1 for time in sorted_times}
    delta = hotness_delta(video_duration)
    killed = {}
    for i, time in enumerate(sorted_times):
        for j, other_time in enumerate(sorted_times):
            if i == j:
                continue
            if time in killed or other_time in killed:
                continue

            i_time = convert_to_seconds(time)
            i_other_time = convert_to_seconds(other_time)

            if abs(i_time - i_other_time) <= delta:
                killed[other_time] = True
                hit_counter[time] += 1
            else:
                pass

    hotspots = [ (time, hit_counter[time]) for time in sorted_times
                                    if time not in killed ]
    return hotspots

def random_shit(duration):
    """
    In rare but terrible scenarios, a youtube video will
    have no timestamped comments, hence rendering this entire
    web application useless. I won't let that happen, this
    method generates radomized timestamps so the user can at least
    feel like they are recieving good content.

    It won't be completely random, I will follow a critera. Some
    clips near the beginning, middle and end.
    """
    rands = set()
    for i in xrange(3):
        rands.add(random.randint(0, duration))

    sorted_rands = sorted(list(rands))
    faked_hotspots = [(convert_to_timestamp(s), 1) for s in sorted_rands]

    hotspots = expand_hotspots(faked_hotspots, duration, 5)
    return hotspots

def expand_hotspots(hotspots, video_duration, max_subclips=10):
    """
    Inputs a list of hotspots, a list of two-tuples with a
    time on slot 1 and the hotness on slot 2.

    Since all video slicing operations on both `moviepi` and the
    `youtubeapi` operate in seconds instead of timestamps, we also
    must make a conversion to pure seconds.

    `max_subclips` denotes the maximum number of subclips that
    we will slice this video into. If the number of subclips
    go over the maximum count, sort and slice out clips which
    don't have a high hotness count.

    A hotclip is a (timestampA, timestampB) tuple.
    So we will be returning a list of tuples.
    """
    # We must divide the delta in half for this function because we are
    # expanding our timestmaps from both sides, so 2*delta will go overboard
    delta = hotness_delta(video_duration)/2
    expanded_spots = []
    lower_bound = 0
    for time, hotness in hotspots:
        seconds = convert_to_seconds(time)
        expanded_spots.append((max(lower_bound, seconds-delta),
                               min(seconds+delta, int(video_duration)-1)))
        lower_bound = min(seconds+delta, int(video_duration)-1)
    if len(expanded_spots) > max_subclips:
        pass  # TODO
    return expanded_spots

def get_clips(timestamps, video_duration):
    """
    Inputs a list of comment timestamps along with total
    video length.

    Combines hot-clips points together to form a summarized video.
    """
    unique_times = unique_timestamps(timestamps)
    sorted_times = sort_timestamps(unique_times)
    hotspots = get_hotspots(sorted_times, video_duration)
    hotclips = expand_hotspots(hotspots, video_duration)
    return hotclips

