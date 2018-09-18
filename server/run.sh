#!/bin/bash
export FLASK_PORT=4850
export PYTHONPATH="$(dirname $PWD)"

function finish {
    if [ -f gunicorn.pid ]; then
        kill $(cat gunicorn.pid)
    fi 
    echo Bye !
}
trap finish EXIT

DEV=false

if [ $DEV = true ];then
    export FTP_HOME="${PWD}/../ftp_dev" 
    mkdir -p ${FTP_HOME}
else
    rm -rdf ${PWD}/../ftp_dev
fi

if [ -z "$REDIS_SERVER_IP" || -z "$REDIS_SERVER_PORT"]; then
    echo Using default Redis env
    export REDIS_SERVER_IP='0.0.0.0'
    export REDIS_SERVER_PORT=6379
fi  

# python3 -u /root/bbb-daemon/server/server.py
pushd ../
git clone https://github.com/vishnubob/wait-for-it.git
pushd wait-for-it
./wait-for-it.sh -t 0 $REDIS_SERVER_IP:$REDIS_SERVER_PORT
popd
popd

# openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

gunicorn --bind 0.0.0.0:${FLASK_PORT} server:app -p gunicorn.pid #-certfile cert.pem --keyfile key.pem