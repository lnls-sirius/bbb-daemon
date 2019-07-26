#!/bin/bash
DAEMON_BASE="/root/bbb-daemon"
PING_CANDIDATES="10.128.255.5"

pushd $DAEMON_BASE/host
    export PYTHONPATH=${DAEMON_BASE}
    CONFIG_PATH=/var/tmp/bbb.bin

    pushd daemon
        ./run_daemon.py \
            --ping-candidates ${PING_CANDIDATES} \
            --configuration-path ${CONFIG_PATH}
    popd
popd
