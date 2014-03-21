#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Written by:
Lucas Ou -- http://codelucas.com
"""
from flask import Flask, request, jsonify, abort
import json
import algorithm
import youtube
from redis import Redis

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')

redis = Redis(host='localhost', port=6379, db=0)

HOTCLIP_CACHE_TIME = 3600 * 24 * 40  # 40 days
MIN_CLIPS = 1


def check_cache(yt_id):
    """
    Check our redis cache to see if the yt_id has already
    been extracted and stored
    """
    prev_yt_dat = eval(redis.get(yt_id) or '{}')
    prev_clips = prev_yt_dat.get('hotclips') or []
    prev_duration = prev_yt_dat.get('duration') or '0'
    prev_duration = int(prev_duration)

    was_cached = (len(prev_clips) >= MIN_CLIPS)
    if was_cached:
        return prev_clips, prev_duration
    return None, None


def check_youtube(yt_id):
    """
    Manually extract data from youtube
    """
    yt_client = youtube.get_client()
    timestamps = youtube.get_timestamp_list(client=yt_client, video_id=yt_id)
    duration = youtube.get_duration(yt_client, video_id=yt_id)
    duration = int(duration)

    hotclips = algorithm.get_clips(timestamps, duration)

    if len(hotclips) < MIN_CLIPS:
        hotclips = hotclips + algorithm.random_shit(duration)
    hotclips = algorithm.sort_seconds(hotclips)

    return hotclips, duration  # , timestamps


def extract(yt_id):
    """
    Method to extract video data from youtube, such as
    timestamps, duration, and our computed hotspot clips.
    """
    clips, duration = check_cache(yt_id)
    if not clips:
        clips, duration = check_youtube(yt_id)
        # cache this data for later
        yt_dat = {'hotclips': clips, 'duration': duration}
        redis.set(yt_id, yt_dat)
        # let's not have the clips expire for now since they take so
        # long to compute
        # redis.setex(yt_id, yt_dat, HOTCLIP_CACHE_TIME)

    return clips, duration


@app.route('/shorten/', methods=['POST'])
def shorten():
    """
    Input a youtube id from the client and we will
    return a jsonified array of subclips. [(s1, e1), (s2, e2)]

    We cache all extracted yt hot clips with their respective yt
    id's. We maintain the 10 most recent hot clips per yt id.
    """
    yt_id = request.form['yt_id']

    if not yt_id:
        abort(404)

    # We are using this weird mixure of json.dumps and flask.jsonify
    # because flask.jsonify does not handle lists or tuples very well,
    # but it is needed for the mime/response headers.

    hotclips, duration = extract(yt_id)

    hotclips_str = json.dumps(hotclips)
    pretty_hotclips = json.dumps(algorithm.all_to_timestamp(hotclips))
    duration_str = algorithm.convert_to_timestamp(duration)

    return jsonify({'hotclips': hotclips_str,
                    'duration': duration_str,
                    'pretty_hotclips': pretty_hotclips
                    })

app.debug = app.config['DEBUG']

if __name__ == '__main__':
    print 'We are running flask backend via main()'
    app.run()
