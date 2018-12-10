#!/bin/bash
DAEMON_BASE="/root/bbb-daemon"
PING_CANDIDATES="10.128.255.5;10.0.6.44;10.0.6.48"

pushd $DAEMON_BASE/host
    export PYTHONPATH=${DAEMON_BASE}
    CONFIG_PATH=${DAEMON_BASE}/bbb.bin

    pushd daemon
        ./run_daemon.py \
            --ping-candidades ${PING_CANDIDATES} \
            --configuration-path ${CONFIG_PATH}
    popd
popd
