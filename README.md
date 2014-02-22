shorten.tv
==========

Official source code for www.shorten.tv, the youtube video summarizer, built with python, flask, ffmpeg, moviepy, and vsummarize.

The `static` directory contains the main web app which users will interact with.
We try to keep everyting as static as possible to minimize the server load. We will handle
video summarization RPC calls with a flask application running on `gunicorn` in the background.

The backend flask code handling video summarization will be in the `backend` directory.

`nginx` will be routing everything besides RPC calls into our static application.
