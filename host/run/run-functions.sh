#!/bin/bash

export DAEMON_BASE=/root/bbb-daemon
export PYTHONPATH=${DAEMON_BASE}
export RSYNC_SERVER="10.128.255.5"
export RSYNC_FAC_SERVER="10.128.254.205"
sed -i -e 's/RSYNC_SERVER.*$/RSYNC_SERVER="10.128.255.5"/' /root/.bashrc
sed -i -e 's/RSYNC_FAC_SERVER.*$/RSYNC_FAC_SERVER="10.128.254.203"/' /root/.bashrc
export RSYNC_LOCAL="/root"
export RSYNC_PORT="873"
export FAC_PATH="/home/fac_files/lnls-sirius"

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
        echo "/etc folder is out of sync. Reboot to fix!"
        # echo Rebooting BBB...
        # shutdown -r now
    fi

    # Updating bbb-daemon files
    echo Synchronizing bbb-daemon files
    ./rsync_beaglebone.sh bbb-daemon
    apt-get install wait-for-it -y
    if [ $? -eq 0 ]; then
        echo New version of bbb-daemon. Making and restarting services...
        pushd ${DAEMON_BASE}/host
            echo "host out of sync"
            # make install
        popd
    fi
popd

pushd ${DAEMON_BASE}/host/function
    echo Starting BBB Function application
    ./init.sh
popd
