#!/usr/bin/env bash

cd /root/wait-for-it/
./wait-for-it.sh $REDIS_SERVER_IP:$REDIS_SERVER_PORT
echo "Redis is UP!"
cd ../bbb-daemon/server/
./run.sh
