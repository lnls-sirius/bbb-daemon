#!/bin/bash

export RSYNC_SERVER="10.0.6.51"
export RSYNC_LOCAL="/root"
export RSYNC_PORT="873"

# Generate the initial device.json
pushd /root/bbb-daemon/host/function/scripts/
    ./initial.py
    cat /opt/device.json
popd

# Updating some contents at etc folder. If so, reboots before continuing
pushd /root/bbb-daemon/host/rsync
    echo Synchronizing etc folder
    ./rsync_beaglebone.sh etc-folder
    if [ $? -eq 0 ]; then
        echo Rebooting BBB...
        shutdown -r now
    fi

# Updating bbb-daemon files
    echo Synchronizing bbb-daemon files
    ./rsync_beaglebone.sh bbb-daemon
popd

pushd /root/bbb-daemon/host/function
    echo Starting BBB Function application
    ./init.sh
popd
