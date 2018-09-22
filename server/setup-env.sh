#!/bin/bash
pushd bbb-daemon-virtualenv/bin
source activate
popd
echo "Using Python 3 on  bbb-daemon-virtualenv ..."
echo "Installing requirements ..."
pip3 install --no-cache-dir -r ../docker/bbb-server/requirements.txt
deactivate
