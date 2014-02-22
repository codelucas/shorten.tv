# Refer to the following link for help:
# http://docs.gunicorn.org/en/latest/settings.html
command = '/home/lucas/www/shorten.tv/shorten-env/bin/gunicorn'
pythonpath = '/home/lucas/www/shorten.tv/shorten-env/shorten.tv'
bind = '127.0.0.1:8090'
workers = 1
user = 'lucas'
accesslog = '/home/lucas/logs/shorten.tv/gunicorn-access.log'
errorlog = '/home/lucas/logs/shorten.tv/gunicorn-error.log'
