#!/bin/bash
export PYTHONPATH="$(dirname $PWD)"

export SERVER_APP_IP='10.0.6.44'
export BBB_UDP_PORT=9876
export BBB_TCP_PORT=9877

# This info should contain a '/'
export FTP_DESTINATION_FOLDER='/root/bbb-daemon-repos/'

python3 daemon.py $SERVER_APP_IP $BBB_UDP_PORT $BBB_TCP_PORT $FTP_DESTINATION_FOLDER
