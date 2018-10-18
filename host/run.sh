#!/bin/bash
export SERVER_APP_IP="10.0.6.44"

'''
pushd ${PWD}/../
    git pull
popd
'''

# Using rsync service
pushd rsync
    echo Synchronizing bbb-daemon files
    ./rsync_beaglebone.sh bbb-daemon
popd

python3 run_daemon.py
