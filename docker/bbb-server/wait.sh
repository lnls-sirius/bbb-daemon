#!/usr/bin/env bash

cd /root/wait-for-it/
echo "Wait for Redis ..."
echo $REDIS_SERVER_IP
echo $REDIS_SERVER_PORT
echo "..."
./wait-for-it.sh -t 0 $REDIS_SERVER_IP:$REDIS_SERVER_PORT
echo "Redis is UP!"
cd /root/bbb-daemon/
git pull
cd /root/bbb-daemon/server/
./run.sh
