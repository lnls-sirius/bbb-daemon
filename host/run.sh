#!/bin/bash
export SERVER_APP_IP="10.0.6.44"

pushd ${PWD}/../
    git pull
popd

python3 run_daemon.py
