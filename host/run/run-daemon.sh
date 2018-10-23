#!/bin/bash
cd ..

export CONFIG_PATH="/root/bbb-daemon/bbb.bin"
export SERVER_ADDR="10.0.6.44"
export BIND_PORT=9877
export PING_PORT=9876
export PING_CANDIDATES="10.0.6.44 10.0.6.48 10.0.6.51"

./run_daemon.py
