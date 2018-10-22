#!/bin/bash
export SERVER_APP_IP="10.0.6.44"

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

#python3 run_daemon.py

pushd /root/bbb-daemon/host/function
    echo Starting BBB application
    ./init.sh
popd
