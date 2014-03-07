#!/usr/bin/env python2.7
"""
Here is shorten.tv's main background task to re-load
and cache popular youtube videos so users have less
wait time when using the webapp.
"""
import requests
import string
import backend
import urllib


letters = list(string.lowercase)  # a, b, c ... z
popular = ["Rihanna", "Usher", "Katy Perry", "Eminem", "Shakira",
           "Taylor Swift", "Akon", "Lady Gaga", "Paramore", "Jay Z",
           "Led Zepplin", "Guns N Roses", "Aerosmith", "Borat",
           "Fallout Boy", "Blink 182", "Justin Bieber", "Drake"]

searches = letters + popular
numb_thumbs = "5"
numb_queries = 5


def encodeURIComponent(input_str):
    """
    Python equivalent of javascript's encodeURIComponent
    """
    return urllib.quote(unicode(input_str).encode('utf-8'), safe='~()*!.\'')


def top_query(term):
    """
    Retrieves top google autocompletion api query
    """
    url = "http://suggestqueries.google.com/complete/search?" + \
          "hl=en&ds=yt&client=youtube&json=t&q=" + \
          encodeURIComponent(term) + "&cp=1"

    results = requests.get(url).json()
    queries = results[1][:5]
    print "Autocomplete results for", results[0], "are", queries
    return queries[0]  # top query


def youtube_top_five(query):
    """
    Retrieves top five yotube video (ids) based on
    a google autocompelte query
    """
    url = "http://gdata.youtube.com/feeds/api/videos?q=" + \
          encodeURIComponent(query) + "&format=5&max-results=" + \
          numb_thumbs + "&v=2&alt=jsonc"

    resp = requests.get(url).json()
    data = resp["data"]
    items = data["items"]
    ids = [video["id"] for video in items]
    return ids


if __name__ == '__main__':
    for search in searches:
        query = top_query(search)
        ids = youtube_top_five(query)

        for yt_id in ids:
            clips, duration = backend.check_youtube(yt_id)
            yt_dat = {'hotclips': clips, 'duration': duration}
            backend.redis.setex(yt_id, yt_dat, backend.HOTCLIP_CACHE_TIME)

            print 'Summarization data cached for id', yt_id, \
                  '~~~~ hotclips:', clips, 'duration:', duration
