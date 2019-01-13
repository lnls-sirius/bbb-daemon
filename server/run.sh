#!/bin/bash
source bbb-daemon-virtualenv/bin/activate

export LC_ALL=en_US.UTF-8
export LC_LANG=en_US.UTF-8
export LANG=en_US.UTF-8
# export FLASK_PORT=4850
# export REDIS_SERVER_IP=0.0.0.0
# export REDIS_SERVER_PORT=6379
export LOG_PATH=$(dirname $PWD)/log/server.log
source run-functions.sh

trap cleanup EXIT

wait-for-redis

mod_wsgi-express start-server \
        --host 0.0.0.0 \
        --port ${FLASK_PORT} \
        --python-path $(dirname $PWD) \
        app.py
