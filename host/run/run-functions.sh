#!/bin/bash

export DAEMON_BASE=/root/bbb-daemon
export PYTHONPATH=${DAEMON_BASE}
export RSYNC_SERVER="10.128.255.5"
export RSYNC_FAC_SERVER="10.128.254.205"
sed -i -e 's/RSYNC_SERVER.*$/RSYNC_SERVER="10.128.255.5"/' /root/.bashrc
sed -i -e 's/RSYNC_FAC_SERVER.*$/RSYNC_FAC_SERVER="10.128.254.205"/' /root/.bashrc
export RSYNC_LOCAL="/root"
export RSYNC_PORT="873"
export FAC_PATH="/home/fac_files/lnls-sirius"



# Generate the initial device.json
pushd ${DAEMON_BASE}/host/function/scripts/
    source ../envs.sh
    # Get Board address
    BOARD_ADDRESS=$(python-sirius -c 'from PRUserial485 import PRUserial485_address;print("{}".format(PRUserial485_address()))')
    # Address 21: MASTER BOARD
    if [ $BOARD_ADDRESS -eq 21 ]
    then
        echo "Disabling external connections for Redis DB"
        python-sirius -c 'from common.database.redisbbb import RedisDatabase;RedisDatabase("localhost").disable_external_connections()'
        ./whoami.py --reset
    fi

    ./Key_dhcp.py   #Verificar se dhcp deve ser configurado

    # Address 17: SLAVE BOARD
#    if [ $BOARD_ADDRESS -eq 17 ]
#    then
#        echo "Enabling external connections for Redis DB"
#        python-sirius -c 'from common.database.redisbbb import RedisDatabase;RedisDatabase("localhost").enable_external_connections()'
#
#    fi
popd


# Install wait-for-it
#apt-get install wait-for-it -y

# Updating etc folder and bbb-daemon if rsync server available.
wait-for-it ${RSYNC_SERVER}:873 --timeout=10
if [ $? -eq 0 ]; then
    pushd ${DAEMON_BASE}/host/rsync
        echo Synchronizing etc folder
        ./rsync_beaglebone.sh etc-folder
        if [ $? -eq 0 ]; then
            echo "/etc folder is out of sync. Reboot to fix!"

        fi

        # Updating bbb-daemon files
        echo Synchronizing bbb-daemon files
        ./rsync_beaglebone.sh bbb-daemon
        if [ $? -eq 0 ]; then
            echo New version of bbb-daemon. Making and restarting services...
            pushd ${DAEMON_BASE}/host
                echo "New bbb-daemon version! Reinstalling and restarting services..."
                make install
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
