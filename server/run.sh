#!/bin/bash
set -x
set -e

pushd ../wait-for-it
    ./wait-for-it.sh -t 0 $REDIS_SERVER_IP:$REDIS_SERVER_PORT
popd


mod_wsgi-express start-server            \
        --host 0.0.0.0                   \
        --port ${FLASK_PORT}             \
        --python-path $(dirname $PWD)    \
        --log-to-terminal                \
        --log-level info                 \
        --user wsgi --group wsgi         \
        app.py
