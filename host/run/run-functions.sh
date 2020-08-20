#!/bin/bash

export DAEMON_BASE=/root/bbb-daemon
export PYTHONPATH=${DAEMON_BASE}
export RSYNC_SERVER="10.128.255.5"
sed -i -e 's/RSYNC_SERVER.*$/RSYNC_SERVER="10.128.255.5"/' /root/.bashrc
export RSYNC_LOCAL="/root"
export RSYNC_PORT="873"

# Generate the initial device.json
pushd ${DAEMON_BASE}/host/function/scripts/
    source ./../envs.sh
    sleep 10
#    ./whoami.py --reset
    ./get_counters_ip.py
    ./key_dhcp.py   #Verificar se dhcp deve ser configurado
    cat /opt/device.json
popd


# Updating etc folder and bbb-daemon if rsync server available.
wait-for-it ${RSYNC_SERVER}:873 --timeout=10
if [ $? -eq 0 ]; then
    pushd ${DAEMON_BASE}/host/rsync
        # Updating bbb-daemon files
        echo Synchronizing bbb-daemon files
        ./rsync_beaglebone.sh bbb-daemon-dev
        if [ $? -eq 0 ]; then
            echo New version of bbb-daemon. Making and restarting services...
            pushd ${DAEMON_BASE}/host
                echo "New bbb-daemon version! Reinstalling and restarting services..."
#                make install
            popd
        fi
    popd
else
    echo "Rsync server not available for bbb-daemon upgrading"
fi


# BBB-function application
pushd ${DAEMON_BASE}/host/function
    echo Starting BBB Function application
    ./init.sh
popd
