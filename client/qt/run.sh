#!/bin/bash
 
PARENT_PATH=$(dirname $PWD)
export PYTHONPATH="$(dirname $PARENT_PATH)"

# Server App Ip Addr
export SERVER_APP_IP=10.0.0.70
# Port to communicate with the server app
export SERVER_APP_COM_PORT=6789

python3 monitor.py $SERVER_APP_IP $SERVER_APP_COM_PORT
