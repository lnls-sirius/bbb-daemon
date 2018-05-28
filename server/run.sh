#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"

export REDIS_SERVER_IP=10.0.6.70
export REDIS_SERVER_PORT=6379

python3 /root/bbb-daemon/server/server.py $REDIS_SERVER_IP $BBB_PING_PORT $REDIS_SERVER_PORT

