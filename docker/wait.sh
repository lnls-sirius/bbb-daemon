#!/usr/bin/env bash

cd /root/wait-for-it/
./wait-for-it.sh www.google.com:80 -- echo "google is up"
cd ../bbb-daemon/server/
./run.sh
