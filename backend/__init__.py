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

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')


def random_shit(hotspots):
    """
    """
    pass


@app.route('/shorten/', methods=['POST'])
def shorten():
    """
    input a youtube id from the client and we will
    return a jsonified array of subclips. [(s1, e1), (s2, e2)]
    """
    yt_id = request.form['yt_id']

    if not yt_id:
        abort(404)

    yt_client = youtube.get_client()
    timestamps = youtube.get_timestamp_list(client=yt_client, video_id=yt_id)
    duration_seconds = youtube.get_duration(yt_client, video_id=yt_id)
    hotclips = algorithm.get_clips(timestamps, duration_seconds)
    hotclips_str = json.dumps(hotclips)
    # prep_json_clips = [list(tup) for tup in hotclips]
    return jsonify({'hotclips': hotclips_str})

app.debug = app.config['DEBUG']

if __name__ == '__main__':
    print 'We are running flask backend via main()'
    app.run()
