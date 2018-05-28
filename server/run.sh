#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"

# These two envs are for debug reasons, remove when using swarm !
export REDIS_SERVER_IP=10.0.6.70
export REDIS_SERVER_PORT=6379

# echo $PYTHONPATH
python3 server.py $REDIS_SERVER_IP $REDIS_SERVER_PORT
