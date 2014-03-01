#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__title__ = 'vSummarize'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import time

def convert_to_timestamp(seconds):
    """
    Converts an integer into a string 'HH:MM:SS'.
    We differ a bit from python's standard time library
    in that if a number is negative, instead of reversing
    back into the 24hr mark, we return 00:00:00.
    """
    if seconds < 0:
        return '00:00:00'
    return time.strftime('%H:%M:%S', time.gmtime(seconds))

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
    seconds = int(tsplit[1])
    minutes = int(tsplit[0])
    return (minutes * 60) + seconds

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
        return 1
    elif video_duration < 120:
        return 3
    elif video_duration < 300:
        return 7
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
    for time, hotness in hotspots:
        seconds = convert_to_seconds(time)
        expanded_spots.append( (seconds-delta, seconds+delta) )
    if len(expanded_spots) > max_subclips:
        pass # TODO
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

