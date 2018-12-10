#!/bin/bash
source bbb-daemon-virtualenv/bin/activate
source run-functions.sh
source envs.sh

trap cleanup EXIT

wait-for-redis

gunicorn --bind 0.0.0.0:${FLASK_PORT} -p gunicorn.pid app:app
# gunicorn --bind 0.0.0.0:${FLASK_PORT} -p gunicorn.pid --certfile cert.pem --keyfile key.pem run_server:wsgi_app
