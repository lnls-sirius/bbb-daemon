#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"

export SERVER_APP_IP=10.0.6.44
export BBB_UDP_PORT=9876
export BBB_TCP_PORT=9877

python3 /root/bbb-daemon/daemon/daemon.py $SERVER_APP_IP $BBB_UDP_PORT $BBB_TCP_PORT
