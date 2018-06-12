#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"


#The enviroment variables bellow are debug only. The production ones are to be set on the .env file to be used on swarm

export REDIS_SERVER_IP=10.0.6.70
export REDIS_SERVER_PORT=6379

export BBB_UDP=9876
export BBB_TCP=9877

export COM_INTERFACE_TCP=6789

export WORKERS_NUM=10

export FLASK_PORT=4850

# The path must be absolute !
export FTP_PORT=1026
export FTP_HOME=/bbb-daemon/types_repository/

python3 -u /root/bbb-daemon/server/server.py $REDIS_SERVER_IP $REDIS_SERVER_PORT $BBB_UDP $BBB_TCP $COM_INTERFACE_TCP $WORKERS_NUM $FLASK_PORT $FTP_HOME

