web: gunicorn slackclient.wsgi --log-file -
worker: celery -A slackclient worker -l INFO -B --loglevel=info
