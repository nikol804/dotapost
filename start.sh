#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn myproject.wsgi --log-file -
