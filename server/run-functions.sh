#!/bin/bash

function cleanup {
    if [ -f gunicorn.pid ]; then
        kill $(cat gunicorn.pid)
    fi 
    if [ $DEV = true ];then
        if [ -d ${PWD}/../ftp_dev ]; then
            rm -rd ${PWD}/../ftp_dev
        fi 
    fi 
    deactivate
    echo Bye !
}

function wait-for-redis {
    pushd ../
        if [ ! -d wait-for-it ];then
            git clone https://github.com/vishnubob/wait-for-it.git
        fi
        pushd wait-for-it
            echo Waiting for Redis at ${REDIS_SERVER_IP}:${REDIS_SERVER_PORT}
            ./wait-for-it.sh -t 0 $REDIS_SERVER_IP:$REDIS_SERVER_PORT
        popd
    popd
}
