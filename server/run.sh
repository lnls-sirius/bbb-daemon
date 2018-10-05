#!/bin/bash
source bbb-daemon-virtualenv/bin/activate
source run-functions.sh
source envs.sh

trap cleanup EXIT

DEV=true

if [ $DEV = true ];then
    export FTP_HOME_DIR="${PWD}/../ftp_dev" 
    export WORKERS_NUM=2
    mkdir -p ${FTP_HOME_DIR}
else
    rm -rdf ${PWD}/../ftp_dev
fi

wait-for-redis

gunicorn --bind 0.0.0.0:${FLASK_PORT} -p gunicorn.pid run_server:wsgi_app
# gunicorn --bind 0.0.0.0:${FLASK_PORT} -p gunicorn.pid --certfile cert.pem --keyfile key.pem run_server:wsgi_app
