#!/usr/bin/env python2.7

# Here is shorten.tv's main background task to re-load
# and cache popular youtube videos so users have less
# wait time when using the webapp.

import requests
import string


letters = list(string.lowercase)
popular = ["Rihanna", "Usher", "Katy Perry", "Eminem", "Shakira",
           "Taylor Swift", "Akon", "Lady Gaga", "Paramore", "Jay Z",
           "Led Zepplin", "Guns N Roses", "Aerosmith", "Borat",
           "Fallout Boy", "Blink 182", "Justin Bieber", "Drake"]
searches = letters + popular

for search in searches:
    url = "http://suggestqueries.google.com/complete/search?" + \
          "hl=en&ds=yt&client=youtube&json=t&q=" + search + "&cp=1"

    results = requests.get(url).json()
    print "Autocomplete results for", results[1], "are", results[1][:5]



