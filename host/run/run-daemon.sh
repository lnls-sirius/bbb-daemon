#!/bin/bash
export DAEMON_BASE=/root/bbb-daemon

pushd $DAEMON_BASE/host
    export PYTHONPATH=${DAEMON_BASE}
    export CONFIG_PATH=${DAEMON_BASE}/bbb.bin
    export SERVER_ADDR="10.128.255.5"
    export BIND_PORT=9877
    export PING_PORT=9876
    export PING_CANDIDATES="10.0.6.44 10.0.6.48 10.128.255.5"

    pushd daemon
        ./run_daemon.py
    popd
popd
