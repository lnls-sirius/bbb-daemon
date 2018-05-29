#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"


#The enviroment variables bellow are debug only. The production ones are to be set on the .env file to be used on swarm

#export REDIS_SERVER_IP=10.0.6.70
#export REDIS_SERVER_PORT=6379

#export BBB_UDP=9876
#export BBB_TCP=9877

#export COM_INTERFACE_TCP=6789

#export WORKERS_NUM=10

python3 /root/bbb-daemon/server/server.py $REDIS_SERVER_IP $BBB_PING_PORT $REDIS_SERVER_PORT $BBB_UDP $BBB_TCP $COM_INTERFACE_TCP $WORKERS_NUM

