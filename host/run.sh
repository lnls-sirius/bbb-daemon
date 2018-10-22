#!/bin/bash
export SERVER_APP_IP="10.0.6.44"

<<<<<<< HEAD

# ----- Updating via Rsync
# etc folder. If so, reboots before continuing
pushd /root/bbb-daemon/host/rsync
    echo Synchronizing etc folder
    ./rsync_beaglebone.sh etc-folder
    if [ $? -eq 0 ]; then
        echo Rebooting BBB...
        shutdown -r now
    fi
# bbb-daemon files
=======
# Updating some contents at etc folder. If so, reboots before continuing
pushd /root/bbb-daemon/host/rsync
    echo Synchronizing etc folder
    ./rsync_beaglebone.sh etc-folder
    if [ $? -eq 0 ]; then
        echo Rebooting BBB...
        shutdown -r now
    fi

# Updating bbb-daemon files
>>>>>>> 27ffffe943a008b194e974cb0e5c6325c682b282
    echo Synchronizing bbb-daemon files
    ./rsync_beaglebone.sh bbb-daemon
popd

<<<<<<< HEAD


# ----- BBB Application
=======
#python3 run_daemon.py

>>>>>>> 27ffffe943a008b194e974cb0e5c6325c682b282
pushd /root/bbb-daemon/host/function
    echo Starting BBB application
    ./init.sh
popd
<<<<<<< HEAD



# ----- BBB Daemon
#python3 run_daemon.py
=======
>>>>>>> 27ffffe943a008b194e974cb0e5c6325c682b282
