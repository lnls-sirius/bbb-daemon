#!/bin/bash

export PYTHONPATH="$(dirname $PWD)"
# echo $PYTHONPATH
python3 server.py $REDIS_SERVER_IP $REDIS_SERVER_PORT
