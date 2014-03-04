Shorten.tv - Video summarization
================================

Official source code for www.shorten.tv, the youtube video summarizer, built with 
python, flask, ffmpeg, moviepy, and the google sdk.

**Architecture**:

We try to keep everything as static as possible to minimize the server load.
The `static` directory is served via `nginx` (default). The static dir  also contains 
the main site which users will interact with.

We will handle video summarization RPC calls with a flask application running 
on `gunicorn` in the background. Because of the intensity of our python background
jobs (querying data from youtube), we will cache as much data as possible on `redis`.

We have a `supervisor` instance watching over our `flask & gunicorn` instance to make sure
it gets restarted incase it dies. Lastly, `nginx` is serving our static files.

The backend flask code handling video summarization will be in the `backend` directory.

`nginx` will be routing everything besides RPC calls into our static application.

**The setup:**

- Set up and install redis-server

`sudo apt-get install redis-server`

- Set up and install nginx

`sudo apt-get install nginx`

- Set up and install supervisor

`sudo apt-get install supervisor`

- Set up and install all of our python dependencies (flask, gunicorn, gdata, requests, etc)

```bash
cd /path/to/project/root
pip install -r requirements.txt
```

Modify the contents of `server/*` and configure the main `nginx` and 
`supervisor` instances to serve up our application. (More descriptive
details to come soon)!

Written by Lucas Ou-Yang -- http://codelucas.com
If you have any questions, don't hesitate to [contact me](http://codelucas.com).
