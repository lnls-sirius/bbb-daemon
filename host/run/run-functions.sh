#!/bin/bash

export DAEMON_BASE=/root/bbb-daemon
export PYTHONPATH=${DAEMON_BASE}
export RSYNC_SERVER="10.128.255.5"
export RSYNC_LOCAL="/root"
export RSYNC_PORT="873"

# Generate the initial device.json
pushd ${DAEMON_BASE}/host/function/scripts/
    ./whoami.py reset
    cat /opt/device.json
popd

# Updating some contents at etc folder. If so, reboots before continuing
pushd ${DAEMON_BASE}/host/rsync
    echo Synchronizing etc folder
    ./rsync_beaglebone.sh etc-folder
    if [ $? -eq 0 ]; then
        echo Rebooting BBB...
        shutdown -r now
    fi

    # Updating bbb-daemon files
    echo Synchronizing bbb-daemon files
    ./rsync_beaglebone.sh bbb-daemon
    if [ $? -eq 0 ]; then
        echo Rebooting BBB...
        shutdown -r now
    fi
popd

pushd ${DAEMON_BASE}/host/function
    echo Starting BBB Function application
    ./init.sh
popd
