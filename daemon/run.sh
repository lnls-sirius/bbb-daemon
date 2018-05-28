#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"

export SERVER_APP_IP=10.0.6.70
export BBB_PING_PORT=9876
export BBB_TCP_PORT=9877

python3 daemon.py $SERVER_APP_IP $BBB_PING_PORT $BBB_TCP_PORT
