#!/bin/bash
source bbb-daemon-virtualenv/bin/activate
source run-functions.sh

trap cleanup EXIT

export FLASK_PORT=4850
export PYTHONPATH=$(dirname $PWD)

export REDIS_SERVER_IP="0.0.0.0"
export REDIS_SERVER_PORT="6379"

export LC_ALL=en_US.UTF-8
export LC_LANG=en_US.UTF-8
export LANG=en_US.UTF-8


DEV=true

if [ $DEV = true ];then
    export FTP_HOME_DIR="${PWD}/../ftp_dev" 
    export WORKERS_NUM=2
    mkdir -p ${FTP_HOME_DIR}
else
    rm -rdf ${PWD}/../ftp_dev
fi

wait-for-redis

gunicorn --bind 0.0.0.0:${FLASK_PORT} -p gunicorn.pid --certfile cert.pem --keyfile key.pem run_server:wsgi_app
