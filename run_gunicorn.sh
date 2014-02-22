#!/bin/bash

exec /home/lucas/www/shorten.tv/shorten-env/bin/gunicorn -c /home/lucas/www/shorten.tv/shorten-env/shorten.tv/server/gunicorn_config.py shortentv.wsgi;
