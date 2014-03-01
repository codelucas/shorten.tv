#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
__title__ = 'vSummarize'
__author__ = 'Lucas Ou-Yang'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014, Lucas Ou-Yang'

import re
from gdata.youtube import service

try:
    from .settings import google_username, google_password
except Exception, e:
    print 'Fails when not using as a module', str(e)
    from settings import google_username, google_password

def comments_generator(client, video_id):
    """
    Directly uses google youtube api to build a generator of comments
    for a particular video. We traverse the comments list via the
    next_link calls. We stop after the first failure.
    """
    try:
        comment_feed = client.GetYouTubeVideoCommentFeed(video_id=video_id)
    except Exception, e:
        print str(e)
        return

    while comment_feed is not None:
        for comment in comment_feed.entry:
             yield comment

        next_link = comment_feed.GetNextLink()

        if next_link is None:
             comment_feed = None
        else:
            try:
                comment_feed = client.GetYouTubeVideoCommentFeed(next_link.href)
            except Exception, e:
                print 'Custom exception', str(e)
                comment_feed = None
                break

def get_duration(client, video_id):
    """
    Returns in string format the duration of this video in seconds.
    """
    video = client.GetYouTubeVideoEntry(video_id=video_id)
    if video and video.media and video.media.duration and video.media.duration.seconds:
        return video.media.duration.seconds
    return ''

def get_yt_comments(client, video_id):
    """
    Extracts out the youtube comments for a particular video in an
    array form. We only note the comment body, not author name, etc.

    There is a start_token glitch in the youtube api which only allows
    us to ge to around comment #600 per video so we stop at 550.

    Also, the standard google api restriction is 1000 most recent comments
    per video anyways. We auth with a custom google application key.
    """
    API_LIMIT = 550
    # import codecs
    # f = codecs.open('comments.txt', 'w', 'utf8')
    count = 1
    ret_comments = []

    for comment in comments_generator(client, video_id):
        if not comment.content.text:
            continue
        # author_name = comment.author[0].name.text
        text = comment.content.text.decode('utf8')
        ret_comments.append(text)

        count += 1
        if count == API_LIMIT:
            break
    return ret_comments

def trim_str_num(s):
    """
    Takes a string in the form of a yt timestamp, \d\d:\d\d, and
    chunks out the whitepace or un-wanted words surrounding it.
    """
    timestamp_arr = [c for c in s if c.isdigit() or c == ':']
    return ''.join(timestamp_arr)

def get_timestamp_list(client, video_id):
    """
    Returns a sorted list of all timestamps present in any comment
    of this selected youtube video.
    """
    vtime_regex = re.compile(u'[\d\s\w]{0,1}\d:\d\d')
    comments = get_yt_comments(client=client, video_id=video_id)
    times = []
    for comment in comments:
        cur_times = vtime_regex.findall(comment)
        clean_times = [trim_str_num(t) for t in cur_times]
        times += clean_times # More pythonic than .extends(..)
    return times

def get_client():
    """
    Returns a gdata client for this youtube video.
    """
    client = service.YouTubeService()
    client.ClientLogin(google_username, google_password)
    return client

if __name__ == '__main__':
    client = get_client()
    video_id = 'p5HXQ1HFDgA'
    timestamps = get_timestamp_list(client=client, video_id=video_id)
    duration_seconds = get_duration(client, video_id=video_id)

    print 'The times are:', timestamps
    print 'The duration is:', duration_seconds
