#!/usr/bin/env python
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

HOTCLIP_CACHE_TIME = 3600 * 24  # one day
MIN_CLIPS = 1


def extract_yt_data(yt_id):
    """
    Method to extract video data from youtube, such as
    timestamps, duration, and our computed hotspot clips.
    """
    yt_client = youtube.get_client()
    timestamps = youtube.get_timestamp_list(client=yt_client, video_id=yt_id)
    duration_seconds = youtube.get_duration(yt_client, video_id=yt_id)

    hotclips = algorithm.get_clips(timestamps, duration_seconds)

    return hotclips, duration_seconds, timestamps

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

    prev_yt_dat = eval(redis.get(yt_id) or '{}')
    prev_clips = prev_yt_dat.get('hotclips') or []
    prev_duration = prev_yt_dat.get('duration') or '0'
    prev_duration = int(prev_duration)

    if len(prev_clips) >= MIN_CLIPS:
        hotclips_str = json.dumps(prev_clips)
        return jsonify({'hotclips': hotclips_str,
                        'duration': algorithm.convert_to_timestamp(prev_duration),
                        'pretty_hotclips': json.dumps(algorithm.all_to_timestamp(prev_clips))
                        })

    # We are using this weird mixure of json.dumps and flask.jsonify
    # because flask.jsonify does not handle lists or tuples very well,
    # but it is needed for the mime/response headers.

    hotclips, duration, timestamps = extract_yt_data(yt_id)
    duration = int(duration)
    if len(hotclips) < MIN_CLIPS:
        hotclips = hotclips + algorithm.random_shit(duration)

    yt_dat = {'hotclips': hotclips, 'duration': duration}
    redis.setex(yt_id, yt_dat, HOTCLIP_CACHE_TIME)

    hotclips_str = json.dumps(hotclips)
    return jsonify({'hotclips': hotclips_str,
                    'duration': algorithm.convert_to_timestamp(prev_duration),
                    'pretty_hotclips': json.dumps(algorithm.all_to_timestamp(prev_clips))
                    })

app.debug = app.config['DEBUG']

if __name__ == '__main__':
    print 'We are running flask backend via main()'
    app.run()
